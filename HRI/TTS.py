from openai import OpenAI
from unrealspeech import UnrealSpeechAPI, play, save
from playsound import playsound
import platform
from Config.config import config
from .utilities import get_audio_length, read_mp3_as_bytes, read_mp3_as_bytes_url
import logging
from pydub import AudioSegment
from io import BytesIO

# aws polly import
from boto3 import Session
from botocore.exceptions import BotoCoreError, ClientError
from contextlib import closing
import os
import sys
import subprocess
from tempfile import gettempdir

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
            self.speed = config["TTS"]["aws"]["speed"]
            self.pitch = config["TTS"]["aws"]["pitch"]
            self.session = Session(profile_name="default")
            self.aws_api = self.session.client("polly")
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

        elif self.api_provider == "aws":
            try:
                # Request speech synthesis
                text = f"""
                    <speak>
                      <prosody rate="{self.speed}" pitch="{self.pitch}">
                        {text}
                      </prosody>
                    </speak>
                """
                response = self.aws_api.synthesize_speech(Text=text, OutputFormat="mp3",
                                                          VoiceId=self.voice_id, TextType="ssml")
            except (BotoCoreError, ClientError) as error:
                # The service returned an error
                logger.error(error)
                return 0

            with closing(response["AudioStream"]) as stream:
                output = os.path.join(gettempdir(), "speech.mp3")

                try:
                    # Open a file for writing the output as a binary stream
                    with open(output, "wb") as file:
                        file.write(stream.read())
                        audio_bytes = read_mp3_as_bytes(output)
                        self.signal_queue.put(get_audio_length(audio_bytes))
                        play(audio_bytes)

                except IOError as error:
                    # Could not write to file, exit gracefully
                    logger.error(error)
                    return 0

        return get_audio_length(audio_bytes)
    