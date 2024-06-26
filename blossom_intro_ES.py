from dotenv import load_dotenv

import TTS
from blossom_interaction import BlossomInterface
from blossom_local_sender import BlossomLocalSender
from config import config
import os
import threading
import time
from pydub import AudioSegment
from pydub.playback import play

load_dotenv()

if config["Blossom"]["status"] == "Enabled":
    if config["Blossom"]["use_network_controller"]:
        bl = BlossomLocalSender()
    else:
         bl = BlossomInterface()

audio_dir = "./blossom_intro_files_ES/" # changed folder with updated files 


def play_mp3(file_path):
    audio = AudioSegment.from_mp3(file_path)
    play(audio)


blossom = [
    "happy/happy_head_bobbing",
    "happy/happy_nodding",
    "happy/happy_5_109",
    "cognitive/extra_08",
    "fear/fear_startled",
    "happy/happy_1_109",
    "cognitive/extra_13",
    "cognitive/extra_14",
    "happy/happy_9_109"
]

audio_files = ['1.mp3', '2.mp3', '3.mp3', '4.mp3', '5.mp3', '6.mp3', '7.mp3', '8.mp3', '9.mp3']


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

            if audio_files[ind] == audio_files[1]:
                time.sleep(5)
            else:
                time.sleep(1.5)

    
play_phrases_and_sequences(blossom, audio_files)
