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

audio_dir = "./blossom_intro_files_mp3/"


def play_mp3(file_path):
    audio = AudioSegment.from_mp3(file_path)
    play(audio)


# speech = [
#     "Hello! I am Blossom, I am a robot from USC.",
#     "I can talk and move my body like this. Because I am a robot, you will hear these sounds that my body makes, I’m sorry!",
#     "Let me welcome you to our research study. It’s great to meet you!",
#     "Let me tell you what we’ll be doing today. We have two fun games lined up.",
#     "I’ll explain each game and give you time to answer. I’ll give you some hints along the way by asking you questions. One of the games will be to describe a picture that you will see on a screen next to me, and the other one to think of words."
#     "Just so you know, I can only focus on one thing at a time, so I won’t be able to answer other questions during the games. But if you don’t understand something or want me to repeat, please let me know!",
#     "Alright, before we begin, my friend Maria will check if you can hear me properly. Talk to you soon! "
# ]

blossom = [
    "cognitive/extra_07",
    "cognitive/extra_08",
    "happy/happy_nodding",
    "cognitive/extra_09",
    "grand/grand4",
    "cognitive/extra_07",
    "cognitive/extra_06",
    "cognitive/extra_08"
]

audio_files = ['new_voice_1.mp3', 'new_voice_2.mp3', 'new_voice_3.mp3', 'new_voice_4.mp3', 'new_voice_5.mp3', 'new_voice_6.mp3', 'new_voice_7.mp3', 'new_voice_8.mp3']


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

        time.sleep(1.5)


play_phrases_and_sequences(blossom, audio_files)
