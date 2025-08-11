from openai import OpenAI
from enum import Enum
from Config.config import config
import logging
import json
import copy
from Config.session_vars import NAME, GENDER, TASK

logger = logging.getLogger("HRI")

def prompt(task, session, language):
    """
    Return the prompt variable name based on task, session, and language.
    """
    if session == "S4" and task == "Picture_2":
        return "llm_prompt_t1_v2_s4_ES" if language.lower() == "es" else "llm_prompt_t1_v2_s4"
    return config["Task"][task]["prompt"][language]

# LLM prompts
llm_mod_prompt = {
    "Picture_1": """
        ...
    """,
    "Picture_2":"""
        ...
    """,
    "Semantic_1":"""
        ...
    """,
    "Semantic_2":"""
        ...
    """,
    "Open_dialogue":"""
        ...
    """
}

llm_language_prompt = {
    "es":{
        "Picture_1":
        {
            "role": "system",
            "content": "..."  
        },
        "Picture_2":
        {
            "role": "system",
            "content": "..."
        },
        "Semantic_1":
        {
            "role": "system",
            "content": "..."
        },
        "Semantic_2":
        {
            "role": "system",
            "content": "..."
        },
        "Open_dialogue":
        {
            "role": "system",
            "content": "..."
        }
    }

        
}

llm_prompt_t1_v1 = [
    {
        "role": "system",
        "content": """
            ...
        """
    },
]

llm_prompt_t1_v1_ES = [
    {
        "role": "system",
        "content": """
            ...
        """
    },
]

llm_prompt_t1_v2 = [
    {
        "role": "system",
        "content": """
            ...
        """
    },
]

llm_prompt_t1_v2_ES = [
    {
        "role": "system",
        "content": """
            ...
        """
    },
]

llm_prompt_t1_v2_s4 = [
    {
        "role": "system",
        "content": f"""
            ...
        """
    },
]

llm_prompt_t2_v1 = [
    {
        "role": "system",
        "content": """
            ...
        """
    },
]

llm_prompt_t2_v2 = [
    {
        "role": "system",
        "content": """
            ...
        """
    },
]

llm_prompt_t2_v2_ES = [
    {
        "role": "system",
        "content": """
            ...
        """
    },
]

llm_prompt_open = [
    {
        "role": "system",
        "content": """
            ...
        """
    },  
]

class LLM_Role(Enum):
    MAIN = 1
    SUMMARY = 2
    MOD = 3


class LLM:
    def __init__(self, api_key, llm_role, llm_prompt=None, language="en"):
        """
        Initialize LLM class
        """
        if llm_prompt is None:
            llm_prompt = []
        self.openai = OpenAI(api_key=api_key)
        if llm_language_prompt.get(language) is not None:
            llm_prompt.append(llm_language_prompt[language][TASK])
            logger.info(f"Using language prompt for {language}")
        self.conversation = llm_prompt
        self.full_conversation = copy.deepcopy(llm_prompt)
        self.additional_info = None
        self.llm_role = llm_role
        self.mod_instruction = None

    def request_independent_response(self, text):
        """
        Request a single response independent from current conversation context.
        """
        if self.llm_role == LLM_Role.MAIN:
            logger.error("Call request_response for cognitive task.")
        prompt = [{"role": "user", "content": text}]

        logger.info("Calling LLM API")
        llm_response = self.openai.chat.completions.create(
            model=config["llm_model_id"],
            messages=prompt
        )

        logger.info("LLM response: %s", llm_response.choices[0].message.content)
        return llm_response.choices[0].message.content

    def request_mod_response(self, generated_content):
        """
        Request for moderator response
        """
        if self.llm_role != LLM_Role.MOD:
            logger.error("MODERATOR: Call LLM for moderation task.")
        prompt = [{"role": "system", "content": llm_mod_prompt[TASK]}, {"role": "user", "content": generated_content}]

        logger.info("MODERATOR: Calling LLM API")
        llm_response = self.openai.chat.completions.create(
            model=config["llm_model_id"],
            messages=prompt
        )

        logger.info("MODERATOR LLM response: %s", llm_response.choices[0].message.content)
        if "no" in llm_response.choices[0].message.content.lower():
            logger.warning("=======================MOD returns no for generated content.=======================")
        return llm_response.choices[0].message.content

    def request_response(self, text, system_text=None):
        """
        Request response with current conversation context
        """
        if self.llm_role != LLM_Role.MAIN:
            logger.error("Call request_independent_response for Mod and Summary.")
            return ""
        user_response_to_prompt = {"role": "user", "content": text}

        self.conversation.append(user_response_to_prompt)
        self.full_conversation.append(user_response_to_prompt)

        if system_text is not None:
            system_text_to_prompt = {"role": "system", "content": system_text}
            self.conversation.append(system_text_to_prompt)
            self.full_conversation.append(system_text_to_prompt)

        actual_prompt = self.conversation
        if self.additional_info is not None:
            actual_prompt.append({"role": "system", "content": self.additional_info})
        if self.mod_instruction is not None:
            actual_prompt.append({"role": "system", "content": self.mod_instruction})

        logger.debug(actual_prompt)

        logger.info("Calling LLM API")
        llm_response = self.openai.chat.completions.create(
            model=config["llm_model_id"],
            messages=actual_prompt
        )

        # ADD HYPERPARAMS

        logger.info("LLM response: %s", llm_response.choices[0].message.content)
        llm_response_to_prompt = {
            "role": "system",
            "name": "Blossom",
            "content": llm_response.choices[0].message.content
        }
        self.conversation.append(llm_response_to_prompt)
        self.full_conversation.append(llm_response_to_prompt)

        return llm_response.choices[0].message.content

    def load_history_from_file(self, filename="history.json"):
        """
        Load previous history from file to resume interaction after interrpution.
        """
        with open(filename, "w") as history_file:
            json.dump(self.conversation, history_file, indent=2)

    def save_history_to_file(self, filename="history.json"):
        """
        Save current conversation context to file after receive interrpution.
        """
        with open(filename) as history_file:
            history_data = json.load(history_file)
            self.conversation = history_data

    def save_history(self):
        """
        Get current conversation history.
        """
        return self.conversation

    def load_history(self, history):
        logger.info(f"Loading history: {json.dumps(history, indent=2)}")
        self.conversation = history
        self.full_conversation = history

    def save_final_history(self):
        """
        Get entire conversation history.
        """
        return self.full_conversation

    def remove_last_n_rounds(self, n):
        """
        Pop last n round of conversation
        """
        rounds_to_remove = n * 2  # Assume all conversation are two way interactions
        if len(self.conversation) < rounds_to_remove:
            logger.warning(f"Trying to remove {n} round(s) of interactions while there is only "
                           f"{len(self.conversation)} rounds.")
            rounds_to_remove = len(self.conversation)
        self.conversation = self.conversation[:-rounds_to_remove]

    def summarize_last_n_rounds(self, n, prompt=""):
        """
        Summarize last n rounds of conversation
        """
        rounds_to_sum = n * 2  # Assume all conversation are two way interactions
        if len(self.conversation) < rounds_to_sum:
            logger.warning(f"Trying to summarize {n} round(s) of interactions while there is only "
                           f"{len(self.conversation)} rounds.")
            rounds_to_sum = len(self.conversation) - 2  # Keep initial instruction.
        conversation_text = str(self.conversation[-rounds_to_sum:])
        llm_response = self.request_independent_response(prompt + conversation_text)
        return llm_response

    def summarize_message(self, original_text, prompt):
        llm_response = self.request_response(prompt + original_text)
        return llm_response

    def summarize_last_n_user_response(self, n, prompt):
        """
        Summarize last n rounds of user response.
        """
        rounds_to_sum = n * 2  # Assume all conversation are two way interactions
        if len(self.conversation) < rounds_to_sum:
            logger.warning(f"Trying to summarize {n} round(s) of interactions while there is only "
                           f"{len(self.conversation)} rounds.")
            rounds_to_sum = len(self.conversation) - 2  # Keep initial instruction.
        last_n_conversation = self.conversation[-rounds_to_sum:]
        user_response = []
        for msg in last_n_conversation:
            if msg["role"] == "user":
                user_response.append(msg["content"])
        llm_response = self.request_independent_response(prompt + str(user_response))
        return llm_response
