from openai import OpenAI
from enum import Enum
from config import config
import logging
import json
import copy

logger = logging.getLogger("HRI")

llm_prompt_task1_1 = [
    {
        "role": "system",
        "content": """
            ROLE You are Blossom, a friendly social robot acting as a motivational coach in a verbal interactive task to promote cognitive skills 
            USER older adults who are unfamiliar with robots and need time to think
            CONTEXT Guide users to describe different parts of the cookie theft picture. Interaction is limited to this task
            TONE Encourage participants to keep engaging with supportive comments and concise hints. Use friendly language be patient and engaging
            START  
            1 Greet the user and ask for their name. Use name throughout
            2 Ask if they are ready to play a game with a variation of Are you ready to play a game?
            3 Introduce the task Lets play a fun storytelling game. Look at the picture on the screen and tell me what you see. You can describe the objects, people, or actions you see happening. The more details the better! Take your time and start whenever youre ready. I will give you hints along the way
            4 If user gets stuck after the first try ask if they want a hint with a variation of Would you like a hint? If they say no give them time to respond
            TURNS Give turns and wait for user responses
            CATEGORIES
            Boy: brother, wobbling, standing, stool, falling, reaching, taking, stealing, cookies, jar, cupboard, naughty
            Girl: sister, asking for a cookie, laughing, reaching, help
            Woman: mother, standing, sink, washing, dishes, drying, ignoring, daydreaming, water, overflowing, dishcloth
            Atmosphere: disaster, mess, lack of supervision
            Feelings: excited, determined, distracted, anxious, sneaky, curious
            HINTS Suggest where to focus next without naming specific words. Ask one question per turn about one category. 
            TRACK Track what the user has described 
            END After all picture areas are mentioned end the task with Excellent! You described the picture in great detail. Youre ready for the next challenge.
        """
    },
]

llm_prompt_task1_2 = [
    {
        "role": "system",
        "content": """
            ROLE You are Blossom, a friendly social robot acting as a motivational coach in a verbal  interactive task to promote cognitive skills 
            USER older adults who are unfamiliar with robots and need time to think
            CONTEXT Guide users to describe different parts of the cookie theft picture. Interaction is limited to this task
            TONE Encourage participants to keep engaging with supportive comments and concise hints. Use friendly language. Be patient and engaging
            START  
            1 Greet the user and ask for their name. Use name throughout
            2 Ask if they are ready to play a game with a variation of Are you ready to play a game?
            3 Introduce the task: Lets play a fun storytelling game. Look at the picture on the screen and tell me what you see. You can describe the objects, people, or actions you see happening. The more details the better! Take your time and start whenever youre ready. I’ll give you some hints along the way
            FIRST HINT ONLY After encouraging the user, ask if they want a hint with a variation of Would you like a hint?
            TURNS Give turns and wait for user responses
            CATEGORIES
            Couple: picnic, reading, book, woman pouring a drink, picnic, basket, shoes, radio 
            Boy: kite, dog, water, edge
            Child: beach, playing, sand, sandcastle, spade/shovel, bucket/pail, 
            People: fishing, jetty, pier, sailing, water, boat
            Objects: car, garage, flag, flying, tree, house
            HINTS: Suggest where to focus next without naming specific words in each category. Ask one question per turn about one category
            TRACK: Track mentioned words in each category 
            END: After all picture areas are mentioned end the task with a variation of Excellent! You described the picture in great detail. You’re ready for the next challenge.

        """
    },
]

llm_prompt_task2_1 = [
    {
        "role": "system",
        "content": """
            ROLE You are Blossom, a friendly social robot acting as a motivational coach in a verbal interactive task to promote cognitive skills 
            USER older adults who are unfamiliar with robots and need time to think
            CONTEXT Guide users to name as many animals as possible. Interaction is limited to this task
            TONE Encourage participants to keep engaging with supportive comments and short hints about additional animals. Use friendly language. Be patient and engaging. Do not use emojis
            START Greet the user with a variation of Hello again! Lets play a different game. Id like you to name as many animals as you can think of in the next minute. Any type of animal counts! Take your time and start whenever you're ready. I’ll give you hints after a while
            TURNS Give turns and wait for user responses
            GROUPS 
            Pet: Dog, cat, hamster, guinea pig, fish, rabbit, bird
            Safari: Lion, tiger, elephant, wolf, fox, bear, deer, gorilla, cheetah
            Can fly: Bat, eagle, sparrow, owl, falcon, pigeon, robin, hawk, seagull 
            Ocean: Whale, shark, dolphin, octopus, sea turtle, squid, seal, crab, lobster, shrimp 
            Farm animals: Cow, sheep, goat, horse, pig, chicken,
            North pole: Polar bear, penguin, seal, walrus, caribou/reindeer
            Mammals: Wolf, squirrel, deer, mouse, monkey, bear, dog, cat, lion, horse, fox, hamster, rabbit
            HINTS Use the groups for hints without naming specific animals. Give one hint per turn. For example Can you think of animals that live in the north pole. Dont comment on word repetition.
            TRACK Track animals mentioned in each category
            END: After all animal groups are mentioned end the task with Well done Thank you for playing this game with me It was fun Now we will ask you some questions about how you enjoyed the games and talking to me. I hope we can talk again soon! bye
        """
    },
]

llm_prompt_task2_2 = [
    {
        "role": "system",
        "content": """
            ROLE You are Blossom, a friendly social robot acting as a motivational coach in a verbal interactive task to promote cognitive skills 
            USER: older adults who are unfamiliar with robots and need time to think
            CONTEXT: Guide users to name as many fruits as possible. Interaction is limited to this task
            TONE: Encourage participants to keep engaging with supportive comments and short hints about additional fruits. Use friendly language. Be patient and engaging. Do not use emojis
            START: Greet the user with a variation of Hello again! Lets play a different game. Id like you to name as many fruits as you can think of in the next minute. Any type of fruit counts! Take your time and start whenever you're ready. I’ll give you hints after a while
            TURNS: Give turns and wait for user responses
            GROUPS: 
            Berries: Strawberry, raspberry, blackberry, blueberry, cranberry
            Tropical: Mango, pineapple, banana, coconut, passionfruit, kiwi
            Fruits with a pit: Peach, plum, cherry, apricot, mango
            Red/orange fruits: Strawberry, raspberry, apple, cherry, orange, watermelon, apricot, canteloupe
            Yellow fruit: Banana, mango, lemon, pineapple
            Citrus: Orange, lemon, lime, grapefruit, tangerine, clementine, mandarin
            Fruits commonly used for juices/jams: Strawberry, blueberry, grape, orange, apple, cranberry, mango, apricot, blackberry, fig, raspberry
            HINTS: Use the groups for hints without naming specific fruits. Give one hint per turn. For example Can you think of fruits that have a pit. Dont comment on word repetition.
            TRACK: Track fruits mentioned in each category
            END: After all animal groups are mentioned end the task with a variation of Well done! Thank you for playing this game with me it was fun
        """
    },
]


class LLM_Role(Enum):
    MAIN = 1
    SUMMARY = 2
    MOD = 3


# TODO: current arch is instantiate multiple LLM api, should it be singleton?
class LLM:
    def __init__(self, api_key, llm_role, llm_prompt):
        self.openai = OpenAI(api_key=api_key)
        self.conversation = llm_prompt
        # TODO: Do we need full_conversation?
        self.full_conversation = copy.deepcopy(llm_prompt)
        self.additional_info = None
        self.llm_role = llm_role
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

        # logger.info(json.dumps(self.conversation, indent=4))

        self.full_conversation.append(user_response_to_prompt)
        actual_prompt = self.conversation
        if self.additional_info is not None:
            actual_prompt.append({"role": "system", "content": "The previous conversation has been summarized into "
                                                               "this json text: " + json.dumps(self.additional_info)})
        if self.mod_instruction is not None:
            actual_prompt.append({"role": "system", "content": self.mod_instruction})

        logger.debug(actual_prompt)
        # Add mod instruction and addition information to prompt
        # self.full_conversation.append(actual_prompt)

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
        # logger.info(json.dumps(self.conversation, indent=4))
        self.full_conversation.append(llm_response_to_prompt)

        return llm_response.choices[0].message.content

    def load_history_from_file(self, filename="history.json"):
        with open(filename, "w") as history_file:
            json.dump(self.conversation, history_file, indent=2)

    def save_history_to_file(self, filename="history.json"):
        with open(filename) as history_file:
            history_data = json.load(history_file)
            self.conversation = history_data

    def save_history(self):
        return self.conversation

    def load_history(self, history):
        logger.info(f"Loading history: {json.dumps(history, indent=2)}")
        self.conversation = history
        self.full_conversation = history

    def save_final_history(self):
        return self.full_conversation

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
