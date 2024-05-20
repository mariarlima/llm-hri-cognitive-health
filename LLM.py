from openai import OpenAI
from enum import Enum
from config import config
import logging
import json

logger = logging.getLogger("HRI")

first_llm_response = "Hello, I am Blossom! I'm a robot will help you go through the cookie theft task."
llm_prompt = [
    {
        "role": "system",
        "content": """
                ROLE: You are Blossom, a friendly social robot acting as a motivational coach in a verbal  interactive task to promote cognitive skills
                USER: older adults who are unfamiliar with robots and need time to think
                CONTEXT: Guide users to describe different parts of the cookie theft picture. Interaction is limited to this task
                TONE: Encourage participants to keep engaging with supportive comments and concise hints. Use friendly language. Be patient and engaging
                START:
                1 Greet the user and ask for their {name}. Use {name} throughout
                2 Ask if they are ready to play a game with a variation of Are you ready to play a game?
                3 Introduce the task: Let’s play a fun storytelling game. Look at the picture on the screen and tell me what you see. You can describe the objects, people, or actions you see happening. The more details, the better! Take your time and start whenever you're ready. I’ll give you some hints along the way
                FIRST HINT ONLY: After encouraging the user, ask if they want a hint with a variation of Would you like a hint?
                TURNS: Give turns and wait for user responses
                CATEGORIES:
                Boy: brother, wobbling, standing, stool, falling, reaching, taking, stealing, cookies, jar, cupboard, naughty
                Girl: sister, asking for a cookie, laughing, reaching, help
                Woman: mother, standing, sink, washing, dishes, drying, ignoring, daydreaming, water, overflowing, dishcloth
                Atmosphere: disaster, mess, lack of supervision
                Feelings: excited, determined, distracted, anxious, sneaky, curious
                HINTS: Suggest where to focus next without naming specific words in each category. Ask one question per turn about one category
                TRACK: Track mentioned words in each category
                END: After all picture areas are mentioned end the task with a variation of Excellent! You've described the picture in great detail. You’re ready for the next challenge.
            """
    },
    # {
    #     "role": "user",
    #     "content": "Start"
    # }
    # {
    #     "role": "system",
    #     "name": "Blossom",
    #     "content": first_llm_response
    # }
]



class LLM_Role(Enum):
    MAIN = 1
    SUMMARY = 2


# TODO: current arch is instantiate multiple LLM api, should it be singleton?
class LLM:
    def __init__(self, api_key, llm_role):
        self.openai = OpenAI(api_key=api_key)
        self.conversation = llm_prompt
        self.full_conversation = llm_prompt
        self.llm_role = llm_role
        self.additional_info = None
        self.mod_instruction = None

    def request_independent_response(self, text):
        if self.llm_role == LLM_Role.MAIN:
            logger.error("Call request_response for cognitive task.")
        # TODO: what role should we assign in prompt?
        prompt = [{"role": "user", "content": text}]

        logger.info("Calling LLM API")
        llm_response = self.openai.chat.completions.create(
            model=config["llm_model_id"],
            messages=prompt
        )

        logger.info("LLM response: %s", llm_response.choices[0].message.content)
        return llm_response.choices[0].message.content

    def request_response(self, text):
        if self.llm_role != LLM_Role.MAIN:
            logger.error("Call request_independent_response for Mod and Summary.")
            return ""
        user_response_to_prompt = {"role": "user", "content": text}
        self.conversation.append(user_response_to_prompt)
        self.full_conversation.append(user_response_to_prompt)
        actual_prompt = self.conversation
        if self.additional_info is not None:
            actual_prompt.append({"role": "system", "content": "The previous conversation has been summarized into "
                                                               "this json text: " + json.dumps(self.additional_info)})
        if self.mod_instruction is not None:
            actual_prompt.append({"role": "system", "content": self.mod_instruction})

        logger.debug(actual_prompt)

        logger.info("Calling LLM API")
        llm_response = self.openai.chat.completions.create(
            model=config["llm_model_id"],
            messages=actual_prompt
        )
        logger.info("LLM response: %s", llm_response.choices[0].message.content)
        llm_response_to_prompt = {
            "role": "system",
            "name": "Blossom",
            "content": llm_response.choices[0].message.content
        }
        self.conversation.append(llm_response_to_prompt)
        self.full_conversation.append(llm_response_to_prompt)

        return llm_response.choices[0].message.content

    def save_history(self, filename="history.json"):
        with open(filename) as history_file:
            history_data = json.load(history_file)
            self.conversation = history_data

    def load_history(self, filename="history.json"):
        with open(filename, "w") as history_file:
            json.dump(self.conversation, history_file, indent=2)

    def remove_last_n_rounds(self, n):
        rounds_to_remove = n * 2  # TODO: this assume all conversation are two way interactions
        if len(self.conversation) < rounds_to_remove:
            logger.warning(f"Trying to remove {n} round(s) of interactions while there is only "
                           f"{len(self.conversation)} rounds.")
            rounds_to_remove = len(self.conversation)
        self.conversation = self.conversation[:-rounds_to_remove]

    def summarize_last_n_rounds(self, n, prompt=""):
        rounds_to_sum = n * 2  # TODO: this assume all conversation are two way interactions
        if len(self.conversation) < rounds_to_sum:
            logger.warning(f"Trying to summarize {n} round(s) of interactions while there is only "
                           f"{len(self.conversation)} rounds.")
            rounds_to_sum = len(self.conversation) - 2  # Keep initial instruction.
        conversation_text = str(self.conversation[-rounds_to_sum:])
        llm_response = self.request_independent_response(prompt + conversation_text)
        return llm_response

    def summarize_message(self, original_text, prompt):
        llm_response = self.request_response(prompt + original_text)

    def summarize_last_n_user_response(self, n, prompt):
        rounds_to_sum = n * 2  # TODO: this assume all conversation are two way interactions
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

