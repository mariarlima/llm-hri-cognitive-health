import logging
from config import config
import torch
import whisper
import speech_recognition as sr
from playsound import playsound

logger = logging.getLogger("HRI")


class STT:
    def __init__(self, mic_index=None):
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

        self.r.pause_threshold = config["STT"]["normal"]["pause_threshold"]
        mic_list = sr.Microphone.list_microphone_names()
        # print(mic_list)

        if 'External Headphones' in mic_list:
            self.mic = sr.Microphone(device_index=mic_list.index('External Headphones'))
            logger.info("Microphone new found!")
        elif 'USBAudio1.0' in mic_list:
            self.mic = sr.Microphone(device_index=mic_list.index('USBAudio1.0'))
            logger.info("Microphone found!")
        elif 'MacBook Pro Microphone' in mic_list:
            self.mic = sr.Microphone(device_index=mic_list.index('MacBook Pro Microphone'))
            logger.warning(f"Extra microphone not found. Using default microphone.")
        else:
            self.mic = sr.Microphone()

    def get_voice_as_text(self, pause_threshold, phrase_time_limit):
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
                    audio = self.r.listen(source, timeout=config["STT"]["timeout"], phrase_time_limit=phrase_time_limit)
                except sr.WaitTimeoutError:
                    response["success"] = False
                    response["error"] = "Listening timed out while waiting for phrase to start"
                    logger.warning("r.listen timeout.")
                    logger.warning(response["error"])
                    return response

            wav_path = 'playback.wav'
            with open(wav_path, "wb") as f:
                f.write(audio.get_wav_data())

            # print(audio_np_array)
            if config["is_playback"]:
                logger.info("Start playback.")
                # Play the saved audio
                playsound(wav_path)

        except Exception as e:
            response["success"] = False
            response["error"] = str(e)
            logger.error(f"An error occurred: {response['error']}")

        # Transcribe

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
