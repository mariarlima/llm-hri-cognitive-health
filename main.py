import os
import queue
import threading
from dotenv import load_dotenv

from config import config
import logging
import logging_config
import time

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
TASK = "Picture_1"
max_duration = 4 * 60  # 4 minutes in seconds

# TODO: implement async audio and https request to achieve a better latency for interaction
if __name__ == '__main__':
    load_dotenv()
    signal_queue = queue.Queue()
    stt = STT.STT()
    # choose appropriate prompt based on task and version/session
    # print(config["STT"]["mic_time_offset"])
    prompt_name = config["Task"][TASK]["prompt"]
    prompt = eval(prompt_name)
    logger.info(f"Choose prompt based on task and version/session: {prompt_name}")
    llm = LLM.LLM(os.getenv("OPENAI_API_KEY"), LLM.LLM_Role.MAIN, llm_prompt=prompt)
    bl = None
    if config["Blossom"]["status"] == "Enabled":
        bl = BlossomInterface()
    if config["TTS"]["api_provider"] == "unrealspeech":
        tts = TTS.TTS(os.getenv("UNREAL_SPEECH_KEY"), signal_queue)
    else:  # fallback to openai tts
        tts = TTS.TTS(os.getenv("OPENAI_API_KEY"), signal_queue, api_provider="openai")
    bl_thread = None

    # Let LLM generate intro
    logger.info("Main interaction loop starts.")
    free_task = False
    end_task = False

    llm_response_text = llm.request_response("Start")
    start_time = time.time()  # Track start time
    bl_thread = threading.Thread(target=bl.do_start_sequence, args=(),
                                 kwargs={"delay_time": config["Blossom"]["delay_intro"]})
    tts_thread = threading.Thread(target=tts.play_text_audio, args=(llm_response_text,))
    tts_thread.start()
    intro_audio_length = signal_queue.get()  # Consume signal here, keep queue empty.
    bl_thread.start()
    time.sleep(intro_audio_length)
    bl.reset()  # Cutoff Blossom's movement after audio ends
    # Main interaction loop
    while True:
        user_input_text = ""
        stt_response = None

        # Case 1: free description
        if free_task:
            free_task = False
            # trigger random behaviour Blossom (start)
        if free_task:
            free_task = False
            if config["Blossom"]["status"] == "Enabled":
                bl_thread = threading.Thread(target=bl.do_start_sequence, args=(),
                                             kwargs={"delay_time": config["Blossom"]["delay"]})
                # bl_thread.start()
            # listen to user
            if config["is_using_voice"]:
                stt_response = stt.get_voice_as_text(
                    phrase_time_limit=config["STT"]["free_speech"]["phrase_time_limit"],
                    pause_threshold=config["STT"]["free_speech"]["pause_threshold"])
            else:
                user_input_text = input("Enter Prompts: ")
        # Case 2: end of interaction (from LLM)
        elif end_task:
            if config["Blossom"]["status"] == "Enabled":
                bl_thread = threading.Thread(target=bl.do_end_sequence, args=(),
                                             kwargs={"delay_time": config["Blossom"]["delay"]})
                # bl_thread.start()
            # end here, will not listen to user
            break

        # Case 3: ongoing interaction/prompting
        else:
            # listen to user
            if config["is_using_voice"]:
                stt_response = stt.get_voice_as_text(
                    phrase_time_limit=config["STT"]["normal"]["phrase_time_limit"],
                    pause_threshold=config["STT"]["normal"]["pause_threshold"])
            else:
                user_input_text = input("Enter Prompts: ")

            # trigger random behaviour Blossom (prompt)
            if config["Blossom"]["status"] == "Enabled":
                bl_thread = threading.Thread(target=bl.do_prompt_sequence, args=(),
                                             kwargs={"delay_time": config["Blossom"]["delay"]})
            else:
                user_input_text = input("Enter Prompts: ")

        if config["is_using_voice"]:
            if stt_response["success"]:
                user_input_text = stt_response["transcription"]["text"]
        # TODO: no blossom exception handling
        # TODO: What should I put in prompt for no voice / stt error? - System message / user message with empty string

        # Check the total interaction time
        elapsed_time = time.time() - start_time
        logger.info(f"Time of HRI: {round(elapsed_time, 2)} s")
        if elapsed_time >= max_duration:
            logger.info("! Max duration reached. Ending interaction now")
            end_task = True
            # break before LLM processes if > max duration
            break

        # LLM process the user input for next interaction turn
        llm_response_text = llm.request_response(user_input_text)

        if config["Task"][TASK]["free_speech_watermark"] in llm_response_text and len(llm_response_text) > 5:
            # TODO: check does this handle the case where people ask for repetition or say something else?
            free_task = True
            logger.info("Free speech watermark detected.")
        if config["Task"][TASK]["end_watermark"] in llm_response_text:
            end_task = True
            logger.info("End of task detected.")

        # TTS audio response
        tts_thread = threading.Thread(target=tts.play_text_audio, args=(llm_response_text,))
        tts_thread.start()
        audio_length = signal_queue.get()  # wait for TTS audio to load
        if config["Blossom"]["status"] == "Enabled":
            bl_thread.start()
        time.sleep(audio_length + config["STT"]["mic_time_offset"])
        bl.reset()  # Cutoff Blossom's movement after audio ends
        logger.info("Main thread wakes up.")

    # play audio for end of task out of main loop
    if end_task:
        end_text = config["Task"][TASK]["end_blossom"]
        bl_thread.start()
        tts.play_text_audio(end_text)
