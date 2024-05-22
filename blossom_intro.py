from dotenv import load_dotenv

import TTS
from blossom_interaction import BlossomInterface
from config import config
import os
import threading
import time

load_dotenv()

if config["TTS"]["api_provider"] == "unrealspeech":
    tts = TTS.TTS(os.getenv("UNREAL_SPEECH_KEY"))

if config["Blossom"]["status"] == "Enabled":
    bl = BlossomInterface()

speech = [
    "Hello! I am Blossom, I am a robot from USC.",
    "I can talk and move my body like this. Because I am a robot, you will hear these sounds that my body makes, I’m sorry!",
    "Let me welcome you to our research study. It’s great to meet you!",
    "Let me tell you what we’ll be doing today. We have two fun games lined up.",
    "I’ll explain each game and give you time to answer. I’ll give you some hints along the way by asking you questions. One of the games will be to describe a picture that you will see on a screen next to me, and the other one to think of words."
    "Just so you know, I can only focus on one thing at a time, so I won’t be able to answer other questions during the games. But if you don’t understand something or want me to repeat, please let me know!",
    "Alright, before we begin, my friend Maria will check if you can hear me properly. Talk to you soon! "
]

blossom = [
    "happy/happy_nodding",
    "happy/happy_20181204_130211",
    "happy/happy_8_10",
    "happy/happy_nodding",
    "cognitive/extra_01",
    "cognitive/extra_02",
    "grand/grand4"
]

for text in speech:
    ind = text.index()
    if config["Blossom"]["status"] == "Enabled":
        bl_thread = threading.Thread(target=bl.do_sequence(seq=blossom[ind]), args=(),
                                     kwargs={"delay_time": config["Blossom"]["delay"]})
        bl_thread.start()

    tts.play_text_audio(text)

    if config["Blossom"]["status"] == "Enabled":
        bl_thread.join()

    time.sleep(1)
