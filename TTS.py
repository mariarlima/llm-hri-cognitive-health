from openai import OpenAI
from unrealspeech import UnrealSpeechAPI, play, save
from playsound import playsound

import logging

logger = logging.getLogger()


class TTS:
    def __init__(self, api_key, api_provider="unrealspeech"):
        self.api_provider = api_provider
        if api_provider == "unrealspeech":
            self.voice_id = "Liv"
            self.bit_rate = "192k"
            self.speed = 0
            self.pitch = 1.1
            self.speech_api = UnrealSpeechAPI(api_key)
        elif api_provider == "openai":
            self.model_id = "tts-1"
            self.voice_id = "alloy"
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
            play(tts_audio_data.content)