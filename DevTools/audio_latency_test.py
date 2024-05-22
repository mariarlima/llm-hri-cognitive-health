from pydub import AudioSegment
from io import BytesIO
import sounddevice as sd
import soundfile as sf
from unrealspeech import UnrealSpeechAPI, play, save
from blossom_interaction import BlossomInterface
import os

def read_mp3_as_bytes(file_path):
    with open(file_path, 'rb') as file:
        audio_bytes = file.read()
    return audio_bytes


def get_audio_length(audio_bytes):
    audio = AudioSegment.from_file(BytesIO(audio_bytes), format="mp3")
    duration_in_milliseconds = len(audio)
    duration_in_seconds = duration_in_milliseconds / 1000
    return duration_in_seconds


