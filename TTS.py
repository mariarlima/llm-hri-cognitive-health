from openai import OpenAI
from unrealspeech import UnrealSpeechAPI, play, save
from playsound import playsound
import platform
from config import config
from utilities import get_audio_length, read_mp3_as_bytes, read_mp3_as_bytes_url
import logging
from pydub import AudioSegment
from io import BytesIO

logger = logging.getLogger("HRI")


class TTS:
    def __init__(self, api_key, signal_queue, api_provider="unrealspeech"):
        self.api_provider = api_provider
        self.signal_queue = signal_queue
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
        elif api_provider == "aws":
            self.voice_id = config["TTS"]["aws"]["voice_id"]
            self.bit_rate = config["TTS"]["aws"]["bit_rate"]
            # self.speech_api = AWSAPI(api_key)
            raise NotImplementedError
        else:
            assert False, "Invalid TTS API Provider."
        logger.info("TTS module initialized.")

    def play_text_audio(self, text):
        logger.info("Calling TTS API...")
        audio_bytes = None
        if self.api_provider == "unrealspeech":
            tts_audio_data = self.speech_api.speech(text=text, voice_id=self.voice_id, bitrate=self.bit_rate,
                                                    speed=self.speed,
                                                    pitch=self.pitch)
            logger.info("Playing TTS Audio...")
            # if platform.system() == "Darwin":
            #     audio_bytes = read_mp3_as_bytes_url(tts_audio_data['OutputUri'])
            #     self.signal_queue.put(get_audio_length(audio_bytes))
            # elif platform.system() == "Windows":
            #     audio_bytes = tts_audio_data
            #     self.signal_queue.put(get_audio_length(audio_bytes))
            audio_bytes = read_mp3_as_bytes_url(tts_audio_data['OutputUri'])
            self.signal_queue.put(get_audio_length(audio_bytes))
            play(tts_audio_data)

        elif self.api_provider == "openai":
            tts_audio_data = self.openai_api.audio.speech.create(
                model=self.model_id,
                voice=self.voice_id,
                input=text
            )
            logger.info("Playing TTS Audio...")
            audio_bytes = tts_audio_data.content
            self.signal_queue.put(get_audio_length(audio_bytes))
            play(tts_audio_data.content)
        return get_audio_length(audio_bytes)
