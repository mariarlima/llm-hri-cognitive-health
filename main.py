import os
import queue
import threading
from dotenv import load_dotenv

from Config.config import config
import logging
import Config.logging_config as logging_config
import time

from HRI.utilities import create_save, load_latest_save, create_final_save, get_integer_input

logger = logging.getLogger("HRI")
logging_config.configure_logger(logger)

logger.info("Logger Initialized.")

# put import here because we need to force logging config set before other modules.
import HRI.STT as STT
import HRI.LLM as LLM
import HRI.TTS as TTS
from Robot.blossom_interaction import BlossomInterface
from Robot.Utilities.blossom_local_sender import BlossomLocalSender
from HRI.LLM import llm_prompt_t1_v1, llm_prompt_t1_v2, llm_prompt_t2_v1, llm_prompt_t2_v2, llm_prompt_t1_v2_s4 # English prompts
from HRI.LLM import llm_prompt_t1_v1_ES, llm_prompt_t1_v2_ES, llm_prompt_t2_v2_ES # Spanish prompts
from HRI.LLM import llm_prompt_open # Open dialogue prompt

from Config.session_vars import PID, TASK, SESSION

if TASK == "Open_dialog":
    max_duration = 3.5 * 60  # 3.5 minutes in seconds
else:
    max_duration = 5 * 60  # 5 minutes in seconds

if __name__ == '__main__':
    load_dotenv()
    signal_queue = queue.Queue()
    language = config["language"]["default"]
    if config["language"].get(PID) is not None:
        language = config["language"][PID]
    # choose appropriate prompt based on task and version/session
    prompt_name = config["Task"][TASK]["prompt"][language]
    if SESSION == "S4" and TASK == "Picture_2":
        prompt_name = "llm_prompt_t1_v2_s4"
        if language == "es":
            prompt_name = "llm_prompt_t1_v2_s4_ES"
    prompt = eval(prompt_name)
    logger.info(f"Choose prompt based on task and version/session: {prompt_name}")
    llm = LLM.LLM(os.getenv("OPENAI_API_KEY"), LLM.LLM_Role.MAIN, llm_prompt=prompt, language=language)
    stt = STT.STT(os.getenv("OPENAI_API_KEY"), PID)
    llm_moderator = LLM.LLM(os.getenv("OPENAI_API_KEY"), LLM.LLM_Role.MOD)
    bl = None
    if config["Blossom"]["status"] == "Enabled":
        if config["Blossom"]["use_network_controller"]:
            bl = BlossomLocalSender()
        else:
            bl = BlossomInterface()
    if language == "es":
        tts = TTS.TTS(os.getenv("AWS_POLLY_KEY"), signal_queue, api_provider="aws")
        logger.info("Using AWS Polly for TTS.")
    elif config["TTS"]["api_provider"] == "unrealspeech":
        tts = TTS.TTS(os.getenv("UNREAL_SPEECH_KEY"), signal_queue)
    else:  # fallback to openai tts
        tts = TTS.TTS(os.getenv("OPENAI_API_KEY"), signal_queue, api_provider="openai")
    bl_thread = None
    bl_thread_target = None
    bl_thread_kwargs = None
    tts_thread = None
    start_time = time.time()
    free_task = False
    end_task = False
    user_input_text = ""
    system_input_text = None
    attempt_times = 0  # Count the number of attempts that MOD returns no for a generated content.

    load_save = False
    load_save_command = input("Enter 'y' to load last save, anything else to start new interaction: ")
    extra_time = get_integer_input("Enter time in second to add more interaction time: ")
    # Load previous save so we can resume interaction without start it over.
    if load_save_command == "y":
        load_save = True
    if load_save:
        save_data = load_latest_save()
        start_time = time.time() - (save_data["elapsed_time"] - extra_time)
        llm.load_history(save_data["conversation_history"])
        llm.additional_info = save_data["additional_info"]
        free_task = save_data["free_task"]
        logger.info("Data loaded.")
    else:
        # Let LLM generate intro
        logger.info("Main interaction loop starts.")

        llm_response_text = llm.request_response("Start")
        start_time = time.time()  # Track start time

        tts_thread = threading.Thread(target=tts.play_text_audio, args=(llm_response_text,))
        tts_thread.start()
        intro_audio_length = signal_queue.get()  # Consume signal here, keep queue empty.

        # handle Blossom activation
        if config["Blossom"]["status"] == "Enabled":
            if TASK == "Picture_1" or TASK == "Picture_2":
                bl_thread = threading.Thread(target=bl.do_prompt_sequence_matching, args=(),
                                             kwargs={"delay_time": config["Blossom"]["delay"],
                                                     "audio_length": intro_audio_length})
                bl_thread.start()
            elif TASK == "Semantic_1" or TASK == "Semantic_2":
                free_task = True
                logger.info("Free task triggered.")
                bl_thread = threading.Thread(target=bl.do_start_sequence, args=(),
                                             kwargs={"delay_time": config["Blossom"]["delay"]})
                bl_thread.start()
        time.sleep(intro_audio_length + config["STT"]["mic_time_offset"])
        if config["Blossom"]["status"] == "Enabled":
            bl.reset()  # Cutoff Blossom's movement after audio ends

    # Main interaction loop
    try:
        while True:
            stt_response = None

            # Case 1: free description
            if free_task:
                logger.info(f"<<<FREE TASK ON>>>")
                free_task = False
                # trigger random behaviour Blossom (start)
                if config["Blossom"]["status"] == "Enabled":
                    bl_thread_target = bl.do_start_sequence
                    bl_thread_kwargs = {"delay_time": config["Blossom"]["delay"]}
                # listen to user
                if config["is_using_voice"]:
                    stt_response = stt.get_voice_as_text(
                        phrase_time_limit=config["STT"]["free_speech"]["phrase_time_limit"][TASK],
                        pause_threshold=config["STT"]["free_speech"]["pause_threshold"][TASK],
                        language=language)

            # Case 2: end of interaction (from LLM)
            elif end_task:
                if config["Blossom"]["status"] == "Enabled":
                    bl_thread_target = bl.do_end_sequence()
                    bl_thread_kwargs = {"delay_time": config["Blossom"]["delay"]}
                    bl_thread = threading.Thread(target=bl_thread_target, args=(), kwargs=bl_thread_kwargs)
                    bl_thread.start()
                # end here, will not listen to user
                break

            # Case 3: ongoing interaction/prompting
            else:
                # listen to user
                if config["is_using_voice"]:
                    pause_threshold = config["STT"]["normal"]["pause_threshold"]["default"]
                    if config["STT"]["normal"]["pause_threshold"].get(PID) is not None:
                        pause_threshold = config["STT"]["normal"]["pause_threshold"][PID]
                    if TASK == "Open_dialogue":
                        logger.info("OPEN DIALOG -- SETTING PARAMS")
                        stt_response = stt.get_voice_as_text(
                            phrase_time_limit=config["STT"]["open_dialog"]["phrase_time_limit"],
                            pause_threshold=config["STT"]["open_dialog"]["pause_threshold"],
                            language=language)
                    else:
                        stt_response = stt.get_voice_as_text(
                            phrase_time_limit=config["STT"]["normal"]["phrase_time_limit"],
                            pause_threshold=pause_threshold,
                            language=language)

                # trigger random behaviour Blossom (prompt)
                if config["Blossom"]["status"] == "Enabled":
                    bl_thread_target = bl.do_prompt_sequence_matching
                    bl_thread_kwargs = {"delay_time": config["Blossom"]["delay"],
                                        "audio_length": 0}

            if config["is_using_voice"]:
                if stt_response["success"]:
                    user_input_text = stt_response["transcription"]["text"]
                    system_input_text = None
                else:
                    logger.warning("STT failed.")
                    logger.error(f"STT error: {stt_response['error']}")
                    user_input_text = ""
                    system_input_text = "No user input is captured, prompt the user again with the same response."
                    logger.info("<<< EMPTY RESPONSE CAPTURED - Prompting user again >>>")

            # Check the total interaction time
            elapsed_time = time.time() - start_time
            logger.info(f"Time of HRI: {round(elapsed_time, 2)} s")
            if elapsed_time >= max_duration:
                # llm.additional_info = f"Max duration reached. Response to user and end interaction."
                logger.info("! Max duration reached. Ending interaction now")
                end_task = True
                # break before LLM processes if > max duration
                continue

            # LLM process the user input for next interaction turn
            llm_response_text = llm.request_response(user_input_text, system_input_text)

            mod_thread = threading.Thread(target=llm_moderator.request_mod_response, args=llm_response_text)
            mod_result = llm_moderator.request_mod_response(llm_response_text)
            if mod_result.lower() == "no":
                logger.info("!!! Content generated by LLM not appropriate. Attempting to regenerate content.")
            
                # Remove last round of conversation history, and regenerate response
                llm.remove_last_n_rounds(1)
                llm_response_text = llm.request_response(user_input_text)
                mod_result = llm_moderator.request_mod_response(llm_response_text)

            # Free speech watermark detection for both tasks

            if config["Task"][TASK]["free_speech_watermark"][language] in llm_response_text.lower():
                free_task = True
                logger.info("Free speech watermark detected.")
                if config["Blossom"]["status"] == "Enabled":
                    bl_thread_target = bl.do_start_sequence
                    bl_thread_kwargs = {"delay_time": config["Blossom"]["delay"]}

            # End of task detection from LLM response
            # for watermark in config["Task"][TASK]["end_watermark"][language]:
            #     if watermark in llm_response_text.lower():
            if config["Task"][TASK]["end_watermark"][language] in llm_response_text.lower():
                    end_task = True
                    logger.info("<<<End of task detected (LLM)>>>")

            # TTS audio response
            tts_thread = threading.Thread(target=tts.play_text_audio, args=(llm_response_text,))
            tts_thread.start()
            audio_length = signal_queue.get()  # wait for TTS audio to load
            if config["Blossom"]["status"] == "Enabled":
                if "audio_length" in bl_thread_kwargs:
                    bl_thread_kwargs["audio_length"] = audio_length
                bl_thread = threading.Thread(target=bl_thread_target, args=(), kwargs=bl_thread_kwargs)
                bl_thread.start()
            time.sleep(audio_length + config["STT"]["mic_time_offset"])
            if config["Blossom"]["status"] == "Enabled":
                bl.reset()  # Cutoff Blossom's movement after audio ends
            logger.info("Main thread wakes up.")
            if end_task:
                save_data = llm.save_final_history()
                save_filename = create_final_save(save_data)
                logger.info(f"Full interaction data saved at {save_filename}")
                exit()

    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt: Backing up...")
        save_data = {
            "elapsed_time": time.time() - start_time,
            "conversation_history": llm.save_history(),
            "additional_info": llm.additional_info,
            "free_task": free_task,
        }
        save_filename = create_save(save_data)
        logger.info(f"Data saved at {save_filename}")

    except Exception as e:
        logger.error(f"Exception occurred: {str(e)}")
        logger.error(e, exc_info=True)
        exit()

    # play audio for end of task out of main loop
    if end_task:
        end_text = config["Task"][TASK]["end_blossom"][language]
        llm.additional_info = f"Max duration of interaction reached. Respond to what the user said first, then end interaction"
        llm_response_text = llm.request_response("")
        logger.info("<<<Additional info added to LLM prompt to end dialoga and respond to user>>>")
        tts.play_text_audio(llm_response_text)
        # tts.play_text_audio(end_text) # not needed because LLM updated prompt with additional info already includes end text
        save_data = llm.save_final_history()
        save_filename = create_final_save(save_data)
        logger.info(f"Full interaction data saved at {save_filename}")
