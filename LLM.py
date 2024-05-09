from openai import OpenAI
import logging

logger = logging.getLogger()

first_llm_response = "Hello, I am Blossom! I'm a robot will help you go through the cookie theft task."
llm_prompt = [
    {
        "role": "system",
        "content": "You are Blossom, a robot that will interact in a picture description task based on the cookie theft picture. You should give hints and encourage while giving turns for the user to reply. Prompt the user with different areas of the picture that havent been mentioned."
    },
    {
        "role": "system",
        "name": "Blossom",
        "content": first_llm_response
    }
]


class LLM:
    def __init__(self, api_key):
        self.openai = OpenAI(api_key=api_key)
        self.conversation = llm_prompt

    def request_response(self, text):
        user_response_to_prompt = {"role": "user", "content": text}
        self.conversation.append(user_response_to_prompt)

        logger.debug(self.conversation)

        logger.info("Calling LLM API")
        llm_response = self.openai.chat.completions.create(
            model="gpt-3.5-turbo",
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
