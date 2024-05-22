from openai import OpenAI
from unrealspeech import UnrealSpeechAPI, play, save
from playsound import playsound
from config import config
import logging

logger = logging.getLogger("HRI")


class TTS:
    def __init__(self, api_key, api_provider="unrealspeech"):
        self.api_provider = api_provider
        if api_provider == "unrealspeech":
            self.voice_id = config["TTS"]["unrealspeech"]["voice_id"]
            self.bit_rate = config["TTS"]["unrealspeech"]["bit_rate"]
            self.speed = config["TTS"]["unrealspeech"]["speed"]
            self.pitch = config["TTS"]["unrealspeech"]["pitch"]
            self.speech_api = UnrealSpeechAPI(api_key)
        elif api_provider == "openai":
            self.model_id = config["TTS"]["openai"]["model_id"]
            self.voice_id = config["TTS"]["openai"]["voice_id"]
            self.openai_api = OpenAI(api_key=api_key)
        else:
            assert False, "Invalid TTS API Provider."
        logger.info("TTS module initialized.")

    def play_text_audio(self, text):
        logger.info("Calling TTS API...")
        if self.api_provider == "unrealspeech":
            tts_audio_data = self.speech_api.speech(text=text, voice_id=self.voice_id, bitrate=self.bit_rate,
                                                    speed=self.speed,
                                                    pitch=self.pitch)
            logger.info("Playing TTS Audio...")
            play(tts_audio_data)
        
        elif self.api_provider == "openai":
            tts_audio_data = self.openai_api.audio.speech.create(
                model=self.model_id,
                voice=self.voice_id,
                input=text
            )
            logger.info("Playing TTS Audio...")
            play(tts_audio_data.content)
