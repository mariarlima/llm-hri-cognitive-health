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
    llm = LLM.LLM(os.getenv("OPENAI_API_KEY"), LLM.LLM_Role.MAIN)
    bl = None
    if config["Blossom"] == "Enabled":
        bl = BlossomInterface()
    if config["TTS"]["api_provider"] == "unrealspeech":
        tts = TTS.TTS(os.getenv("UNREAL_SPEECH_KEY"))
    else:  # fallback to openai tts
        tts = TTS.TTS(os.getenv("OPENAI_API_KEY"), api_provider="openai")

    # Let LLM generates intro
    logger.info("Main interaction loop starts.")
    free_speech = False
    llm_response_text = llm.request_response("Start")
    tts.play_text_audio(llm_response_text)
    while True:
        user_input_text = ""
        stt_response = None
        if free_speech:
            free_speech = False
            stt_response = stt.get_voice_as_text(phrase_time_limit=60, pause_threshold=7)
        else:
            stt_response = stt.get_voice_as_text(phrase_time_limit=0, pause_threshold=4)
        if stt_response["success"]:
            user_input_text = stt_response["transcription"]["text"]
        # TODO: no blossom exception handling
        # TODO: What should I put in prompt for no voice / stt error? - System message / user message with empty string
        # user_input_text = input("Enter prompt: ")
        llm_response_text = llm.request_response(user_input_text)
        if config["Task"]["Picture"]["free_speech_watermark"] in llm_response_text:
            free_speech = True
            # llm_response_text.replace(config["free_speech_watermark"], "")
            logger.info("Free speech watermark detected.")
        if config["Blossom"] == "Enabled":
            bl_thread = threading.Thread(target=bl.do_sequence, args=("grand/grand1",), kwargs={"delay_time": 10})
            bl_thread.start()

        tts.play_text_audio(llm_response_text)

        if config["Blossom"] == "Enabled":
            bl_thread.join()
