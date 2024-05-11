import os
from dotenv import load_dotenv

from config import config
import logging
import logging_config

logging_config.configure_logging()
logger = logging.getLogger()

logger.info("Logger Initialized.")

# put import here because we need to force logging config set before other modules.
import STT
import LLM
import TTS
from blossom_interaction import BlossomInterface

# TODO: implement async audio and https request to achieve a better latency for interaction
if __name__ == '__main__':
    load_dotenv()
    stt = STT.STT()
    llm = LLM.LLM(os.getenv("OPENAI_API_KEY"))
    bl = BlossomInterface()
    if config["TTS"]["api_provider"] == "unrealspeech":
        tts = TTS.TTS(os.getenv("UNREAL_SPEECH_KEY"))
    else:  # fallback to openai tts
        tts = TTS.TTS(os.getenv("OPENAI_API_KEY"), api_provider="openai")

    # Since first response is pre-defined, play it through tts module.
    # tts.play_text_audio(LLM.first_llm_response)
    logger.info("Main interaction loop starts.")
    isFIrstRound = True
    llm_response_text = llm.request_response("Start")
    tts.play_text_audio(llm_response_text)
    while True:
        if isFIrstRound:
            isFIrstRound = False
            user_input_text = stt.get_voice_as_text(phrase_time_limit=60, pause_threshold=10)["transcription"]["text"]
        else:
            user_input_text = stt.get_voice_as_text(phrase_time_limit=0, pause_threshold=3)["transcription"]["text"]
        # TODO: catch stt error here, we assume stt always works here
        # TODO: catch no voice reply here
        # TODO: no blossom exception handling
        llm_response_text = llm.request_response(user_input_text)
        # llm_response_text = llm.request_response("What is a cookie theft task?")
        bl.do_idle_sequence()

        # llm_response_text = "A sonnet is a poetic form that originated in the poetry composed at the Court of the Holy Roman Emperor Frederick II in the Sicilian city of Palermo. The 13th-century poet and notary Giacomo da Lentini is credited with the sonnet's invention, and the Sicilian School of poets who surrounded him then spread the form to the mainland. The earliest sonnets, however, no longer survive in the original Sicilian language, but only after being translated into Tuscan dialect."
        bl.do_sequence("grand/grand1")
        tts.play_text_audio(llm_response_text)

