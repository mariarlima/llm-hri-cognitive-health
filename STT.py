import logging
from config import config

import torch
# import numpy as np
import whisper
import speech_recognition as sr
from playsound import playsound

logger = logging.getLogger()


class STT:
    def __init__(self):
        # Initialize whisper model
        if torch.cuda.is_available():
            device = torch.device("cuda")
            logger.info("PyTorch is using CUDA.")
        else:
            device = "cpu"
            logger.warning("PyTorch is using CPU.")
        logger.info("Loading whisper model with ID: %s", config["whisper_model_id"])
        self.whisper_model = whisper.load_model(config["whisper_model_id"]).to(device)
        logger.info("Whisper model loaded.")

        # TODO: play with energy level.
        logger.info("Initializing Mic...")
        self.r = sr.Recognizer()

        self.r.pause_threshold = config["STT"]["pause_threshold"]
        self.mic = sr.Microphone()

    def get_voice_as_text(self, pause_threshold=5, phrase_time_limit=0):
        with self.mic as source:
            self.r.pause_threshold = pause_threshold
            self.r.adjust_for_ambient_noise(source, 1)
            logger.info("listening...")
            # Timeout: max time r.listen will wait until a speech is picked up
            # Phrase time limit: max duration of audio clip being recorded
            audio = self.r.listen(source, timeout=10, phrase_time_limit=phrase_time_limit)

        # TODO: handle r.listen exception here
        wav_path = 'playback.wav'
        with open(wav_path, "wb") as f:
            f.write(audio.get_wav_data())

        # print(audio_np_array)
        if config["is_playback"]:
            logger.info("Start playback.")
            # Play the saved audio
            playsound(wav_path)

        # Transcribe
        response = {
            "success": True,
            "error": None,
            "transcription": None
        }

        logger.info("Transcribing...")
        # try recognizing the speech in the recording
        # if a RequestError or UnknownValueError exception is caught,
        #     update the response object accordingly
        try:
            response["transcription"] = self.whisper_model.transcribe('playback.wav')
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
