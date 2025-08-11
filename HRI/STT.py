import logging

from openai import OpenAI

from Config.config import config
import torch
import whisper
import speech_recognition as sr
from playsound import playsound

logger = logging.getLogger("HRI")


class STT:
    def __init__(self, api_key, pid):
        # Initialize whisper API
        self.openai_api = OpenAI(api_key=api_key)
        self.pid = pid
        # Initialize whisper model
        if torch.cuda.is_available():
            self.device = torch.device("cuda")
            logger.info("PyTorch is using CUDA.")
        else:
            self.device = torch.device("cpu")
            logger.warning("PyTorch is using CPU.")

        self.whisper_model_id = config["whisper_model_id"].get(self.pid, config["whisper_model_id"]["default"])
        logger.info("Loading whisper model with ID: %s", self.whisper_model_id)

        self.whisper_model = whisper.load_model(self.whisper_model_id).to(self.device)
        logger.info("Whisper model loaded.")

        logger.info("Initializing Mic...")
        self.r = sr.Recognizer()

        self.r.pause_threshold = config["STT"]["normal"]["pause_threshold"] 

        try:
            mic_list = sr.Microphone.list_microphone_names()
            logger.debug("Available microphones: %s", mic_list)

            preferred = [
                "USBAudio1.0",
                "External Headphones",
                "MacBook Pro Microphone",
            ]
            chosen_index = None
            for name in preferred:
                if name in mic_list:
                    chosen_index = mic_list.index(name)
                    logger.info("Selected microphone: %s", name)
                    break

            self.mic = sr.Microphone(device_index=chosen_index) if chosen_index is not None else sr.Microphone()
            logger.info("Microphone ready: %s", getattr(self.mic, "device_index", "default"))
                
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            self.mic = sr.Microphone()
        

    def get_voice_as_text(self, pause_threshold, phrase_time_limit, use_api=False, language="en"):
        """
        Listen to user speech and transcribe it to text using Whisper API.
        """
        response = {
            "success": True,
            "error": None,
            "transcription": None
        }
        try:
            with self.mic as source:
                self.r.pause_threshold = pause_threshold
                self.r.adjust_for_ambient_noise(source, 1)  # adjust if too noisy
                logger.info("listening...")
                # Timeout: max time r.listen will wait until a speech is picked up
                # Phrase time limit: max duration of audio clip being recorded
                try:
                    audio = self.r.listen(
                        source, 
                        timeout=config["STT"]["timeout"], 
                        phrase_time_limit=phrase_time_limit
                    )
                except sr.WaitTimeoutError:
                    response.update({
                        "success": False,
                        "error": "Listening timed out while waiting for phrase to start",
                    })
                    logger.warning("listen() timeout: %s", response["error"])
                    return response

            wav_path = 'playback.wav'
            with open(wav_path, "wb") as f:
                logger.info("Playback enabled; playing captured audio...")
                try:
                    playsound(wav_path)
                except Exception as play_err:
                    # NOTE: playback should not fail the whole STT path
                    logger.warning("Audio playback failed: %s", str(play_err))

        # Transcribe
        if use_api:
            logger.info("Calling OpenAI Transcription API...")
            audio_file = open("playback.wav", "rb")
            transcript = self.openai_api.audio.transcriptions.create(
                file=audio_file,
                model="whisper-1",
                response_format="text"
            )
        else:
            logger.info("Transcribing...")
            try:
                response["transcription"] = self.whisper_model.transcribe('playback.wav', language=language)
            except sr.RequestError:
                # API was unreachable or unresponsive
                response["success"] = False
                response["error"] = "API unavailable"
            except sr.UnknownValueError:
                # speech was unintelligible
                response["error"] = "Unable to recognize speech"

            if response["success"]:
                logger.info("You said: %s", response["transcription"]["text"])
            else:
                logger.warning("Transcribe failed.")
                logger.warning("%s", response["error"])

        return response
