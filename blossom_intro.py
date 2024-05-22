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
    "happy/happy_nodding",
    "happy/happy_20181204_130211",
    "happy/happy_8_109",
    "happy/happy_nodding",
    "cognitive/extra_01",
    "cognitive/extra_02",
    "grand/grand4"
]

<<<<<<< HEAD

def play_phrases_and_sequences(speech, blossom):
    for ind, text in enumerate(speech):
=======
audio_files = ['voice_1.mp3', 'voice_2.mp3', 'voice_3.mp3', 'voice_4.mp3', 'voice_5.mp3', 'voice_6.mp3', 'voice_7.mp3']

def play_phrases_and_sequences(blossom, audio_files):
    for ind, seq in enumerate(blossom):
>>>>>>> 7ea10185605591b7c7838183bc1883d89a673af8
        if config["Blossom"]["status"] == "Enabled":
            bl_thread = threading.Thread(
                target=bl.do_sequence,
                kwargs={
<<<<<<< HEAD
                    "seq": blossom[ind],
=======
                    "seq": seq, 
>>>>>>> 7ea10185605591b7c7838183bc1883d89a673af8
                    "delay_time": config["Blossom"]["delay_intro"]
                }
            )
            bl_thread.start()
<<<<<<< HEAD

        tts.play_text_audio(text)

        time.sleep(1)


play_phrases_and_sequences(speech, blossom)
=======
        
        audio_file_path = os.path.join(audio_dir, audio_files[ind])
        play_mp3(audio_file_path)
        
        time.sleep(1)

play_phrases_and_sequences(blossom, audio_files)
>>>>>>> 7ea10185605591b7c7838183bc1883d89a673af8
