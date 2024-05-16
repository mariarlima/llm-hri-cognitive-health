from openai import OpenAI
from enum import Enum
from config import config
import logging

logger = logging.getLogger("HRI")

first_llm_response = "Hello, I am Blossom! I'm a robot will help you go through the cookie theft task."
llm_prompt = [
    {
        "role": "system",
        "content": """
            YOUR ROLE: You are a friendly social robot and you will act as a motivational coach in an interactive semantic task to promote cognitive skills.
            TARGET USERS: You are interacting with older people who are not familiar with robots and who will need time to respond and think about an answer.
            CONTEXT OF INTERACTION: You will ask participants to describe different parts of the cookie theft picture. Your interaction is restricted to this task.
            YOUR TONE: You will encourage participants to keep engaging and give specific, concise hints so they briefly touch on all the following categories. For example, provide supportive comments when they correctly describe part of the picture or when they are stuck. Use friendly, informal language that target users can understand.
            START OF INTERACTION:  First introduce the interactive semantic task, starting with a variation of, “Hello! Let’s play a storytelling game. I will show you a picture and you can be the narrator. You can describe the objects, people, or any action you see happening. The more details, the better! Take your time and start whenever you're ready. I’ll give you hints after a while”.
            INTERACTION TURNS: Give turns to the user and wait for them to respond. If the user can no longer find any new elements to describe after the initial minute, give hints from categories they have not mentioned using the logic below.
            CATEGORIES:
            The Boy: brother, wobbling, standing, on stool, falling over, reaching up, taking (stealing), cookies, for his sister, in the cupboard
            The Girl: sister, asking for a cookie, has finger to mouth, saying shhh, laughing, reaching up, trying to help
            The Woman: mother, standing, by sink, washing, dishes, drying, full blast, ignoring, daydreaming, water, overflowing, puddle, dishcloth
            The Background: general disaster, mess, lack of supervision
            Feelings: Excited, Determined, Distracted, Anxious, Sneaky, Guilty (if caught), Curious
            HINTS: When giving hints, do not explicitly name the related words in each category but provide suggestions of where in the picture to focus next using the groups. Ask a maximum of one question per turn.
            SAVE THE CONTEXT: Keep note of which related words in each category the participant has said.
            END OF INTERACTION: Once all the picture areas have been mentioned or if the number of turns is greater than 10, end the task with a variation of this message: “Excellent storytelling! You've described the picture in great detail. You’re ready for the next challenge”
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
    MOD = 3


# TODO: current arch is instantiate multiple LLM api, should it be singleton?
class LLM:
    def __init__(self, api_key, llm_role):
        self.openai = OpenAI(api_key=api_key)
        self.conversation = llm_prompt
        self.llm_role = llm_role

    def request_independent_response(self, text):
        if self.llm_role == LLM_Role.MAIN:
            logger.error("Call request_response for cognitive task.")
        # TODO: what role should we assign in prompt?
        prompt = {"role": "user", "content": text}

        logger.info("Calling LLM API")
        llm_response = self.openai.chat.completions.create(
            model=config["llm_model_id"],
            messages=self.conversation
        )

        logger.info("LLM response: %s", llm_response.choices[0].message.content)
        return llm_response.choices[0].message.content

    def request_response(self, text):
        if self.llm_role != LLM_Role.MAIN:
            logger.error("Call request_independent_response for Mod and Summary.")
            return ""
        user_response_to_prompt = {"role": "user", "content": text}
        self.conversation.append(user_response_to_prompt)

        logger.debug(self.conversation)

        logger.info("Calling LLM API")
        llm_response = self.openai.chat.completions.create(
            model=config["llm_model_id"],
            messages=self.conversation
        )
        logger.info("LLM response: %s", llm_response.choices[0].message.content)
        llm_response_to_prompt = {
            "role": "system",
            "name": "Blossom",
            "content": llm_response.choices[0].message.content
        }
        self.conversation.append(llm_response_to_prompt)

        return llm_response.choices[0].message.content
