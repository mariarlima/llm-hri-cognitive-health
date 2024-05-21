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
from LLM import llm_prompt_task1_1, llm_prompt_task1_2, llm_prompt_task2_1, llm_prompt_task2_2

# Choose from "Picture_1", "Picture_2", "Semantic_1", "Semantic_2"
TASK = "Semantic_1"

# TODO: implement async audio and https request to achieve a better latency for interaction
if __name__ == '__main__':
    load_dotenv()
    stt = STT.STT()
    # choose appropriate prompt based on task and version/session
    prompt_name = config["Task"][TASK]["prompt"]
    prompt = eval(prompt_name)
    logger.info(f"Choose prompt based on task and version/session: {prompt_name}")
    llm = LLM.LLM(os.getenv("OPENAI_API_KEY"), LLM.LLM_Role.MAIN, llm_prompt=prompt)
    bl = None
    if config["Blossom"]["status"] == "Enabled":
        bl = BlossomInterface()
    if config["TTS"]["api_provider"] == "unrealspeech":
        tts = TTS.TTS(os.getenv("UNREAL_SPEECH_KEY"))
    else:  # fallback to openai tts
        tts = TTS.TTS(os.getenv("OPENAI_API_KEY"), api_provider="openai")

    # bl_thread = threading.Thread(target=bl.do_start_sequence(), args=(), kwargs={"delay_time": 5})
    # bl_thread.start()
    # bl_thread.join()
    # input()

    # Let LLM generate intro
    logger.info("Main interaction loop starts.")
    free_task = False
    end_task = False
    llm_response_text = llm.request_response("Start")
    tts.play_text_audio(llm_response_text)
    while True:
        user_input_text = ""
        stt_response = None
        if free_task:
            free_task = False
            if config["Blossom"]["status"] == "Enabled":
                bl_thread = threading.Thread(target=bl.do_start_sequence(), args=(),
                                             kwargs={"delay_time": config["Blossom"]["delay"]})
                bl_thread.start()
            stt_response = stt.get_voice_as_text(phrase_time_limit=config["STT"]["free_speech"]["phrase_time_limit"],
                                                 pause_threshold=config["STT"]["free_speech"]["pause_threshold"])
        elif end_task:
            # end_task = False
            if config["Blossom"]["status"] == "Enabled":
                bl_thread = threading.Thread(target=bl.do_end_sequence(), args=(),
                                             kwargs={"delay_time": config["Blossom"]["delay"]})
                bl_thread.start()
            # stt_response = stt.get_voice_as_text(phrase_time_limit=60, pause_threshold=10)
            break
        else:
            # print("Available microphones:", stt.list_microphones())
            stt_response = stt.get_voice_as_text(phrase_time_limit=config["STT"]["free_speech"]["phrase_time_limit"],
                                                 pause_threshold=config["STT"]["free_speech"]["pause_threshold"])
            if config["Blossom"]["status"] == "Enabled":
                bl_thread = threading.Thread(target=bl.do_prompt_sequence(), args=(),
                                             kwargs={"delay_time": config["Blossom"]["delay"]})
                bl_thread.start()
            # print(stt_response)
        if stt_response["success"]:
            user_input_text = stt_response["transcription"]["text"]
        # TODO: no blossom exception handling
        # TODO: What should I put in prompt for no voice / stt error? - System message / user message with empty string
        llm_response_text = llm.request_response(user_input_text)
        if config["Task"][TASK]["free_speech_watermark"] in llm_response_text and len(
                llm_response_text) > 5:  # does this handle the case where people ask for repetition or say something else?
            free_task = True
            logger.info("Free speech watermark detected.")
        if config["Task"][TASK]["end_watermark"] in llm_response_text:
            end_task = True
            logger.info("End of task detected.")
        if config["Blossom"]["status"] == "Enabled":
            bl_thread = threading.Thread(target=bl.do_sequence, args=("grand/grand1",),
                                         kwargs={"delay_time": config["Blossom"]["delay"]})
            bl_thread.start()

        tts.play_text_audio(llm_response_text)

        if config["Blossom"]["status"] == "Enabled":
            bl_thread.join()

    if end_task:
        tts.play_text_audio(llm_response_text)
    if config["Blossom"]["status"] == "Enabled":
        bl_thread.join()
