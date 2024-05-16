import os
import threading
from dotenv import load_dotenv

from config import config
import logging
import logging_config

# logging_config.configure_logging()
logger = logging.getLogger("HRI")
logging_config.configure_logger(logger)

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
    bl = None
    if config["Blossom"] == "Enabled":
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
        user_input_text = ""
        stt_response = None
        if isFIrstRound:
            isFIrstRound = False
            stt_response = stt.get_voice_as_text(phrase_time_limit=60, pause_threshold=10)
        else:
            stt_response = stt.get_voice_as_text(phrase_time_limit=0, pause_threshold=3)
        if stt_response["success"]:
            user_input_text = stt_response["transcription"]["text"]
        # TODO: no blossom exception handling
        # TODO: What should I put in prompt for no voice / stt error? - System message / user message with empty string
        llm_response_text = llm.request_response(user_input_text)
        # llm_response_text = llm.request_response("What is a cookie theft task?")
        if config["Blossom"] == "Enabled":
            bl_thread = threading.Thread(target=bl.do_sequence("grand/grand1", delay_time=2))
            # bl.do_idle_sequence()
            # bl.do_sequence("grand/grand1")
            bl_thread.start()

        # llm_response_text = "A sonnet is a poetic form that originated in the poetry composed at the Court of the Holy Roman Emperor Frederick II in the Sicilian city of Palermo. The 13th-century poet and notary Giacomo da Lentini is credited with the sonnet's invention, and the Sicilian School of poets who surrounded him then spread the form to the mainland. The earliest sonnets, however, no longer survive in the original Sicilian language, but only after being translated into Tuscan dialect."
        tts.play_text_audio(llm_response_text)

        if config["Blossom"] == "Enabled":
            bl_thread.join()

