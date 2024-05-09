import os
from dotenv import load_dotenv

import logging
import logging_config

logging_config.configure_logging()
logger = logging.getLogger()

logger.info("Logger Initialized.")

# put import here because we need to force logging config set before other modules.
import STT
import LLM
import TTS

# TODO: implement async audio and https request to achieve a better latency for interaction
if __name__ == '__main__':
    load_dotenv()
    stt = STT.STT()
    llm = LLM.LLM(os.getenv("OPENAI_API_KEY"))
    # tts = TTS.TTS(os.getenv("UNREAL_SPEECH_KEY"))
    tts = TTS.TTS(os.getenv("OPENAI_API_KEY"), api_provider="openai")

    # Since first response is pre-defined, play it through tts module.
    tts.play_text_audio(LLM.first_llm_response)
    logger.info("Main interaction loop starts.")
    while True:
        user_input_text = stt.get_voice_as_text()["transcription"]["text"]
        # TODO: catch stt error here, we assume stt always works here
        llm_response_text = llm.request_response(user_input_text)
        # llm_response_text = llm.request_response("What is a cookie theft task?")
        tts.play_text_audio(llm_response_text)
