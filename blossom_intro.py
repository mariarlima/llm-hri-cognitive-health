from dotenv import load_dotenv

import TTS
from blossom_interaction import BlossomInterface
from config import config
import os
import threading
import time
from pydub import AudioSegment
from pydub.playback import play

load_dotenv()

if config["Blossom"]["status"] == "Enabled":
    bl = BlossomInterface()

audio_dir = "./blossom_intro_files_mp3/upd/" # changed folder with updated files 


def play_mp3(file_path):
    audio = AudioSegment.from_mp3(file_path)
    play(audio)


blossom = [
    "cognitive/extra_07",
    "cognitive/extra_08",
    "happy/happy_nodding",
    "cognitive/extra_09",
    "cognitive/extra_11",
    "cognitive/extra_07",
    "cognitive/extra_06",
    "cognitive/extra_10",
    "cognitive/extra_08"
]

audio_files = ['new_voice_1.mp3', 'new_voice_2.mp3', 'new_voice_3.mp3', 'new_voice_4.mp3', 'new_voice_5.mp3', 'new_voice_6.mp3', 'new_voice_7.mp3', 'new_voice_8.mp3', 'new_voice_9.mp3']


def play_phrases_and_sequences(blossom, audio_files):
    for ind, seq in enumerate(blossom):
        if config["Blossom"]["status"] == "Enabled":
            bl_thread = threading.Thread(
                target=bl.do_sequence,
                kwargs={
                    "seq": seq,
                    "delay_time": config["Blossom"]["delay_intro"]
                }
            )
            bl_thread.start()

        audio_file_path = os.path.join(audio_dir, audio_files[ind])
        play_mp3(audio_file_path)

        if audio_files[ind] == audio_files[1]:
            time.sleep(5)
        else:
            time.sleep(1.5)

    
play_phrases_and_sequences(blossom, audio_files)
