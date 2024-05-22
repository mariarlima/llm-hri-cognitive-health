import random
import sys
import time
import logging
from config import config

sys.path.append("./blossom-public")
from blossompy import Blossom

logger = logging.getLogger("HRI")

class BlossomInterface:
    def __init__(self):
        self.bl = Blossom(sequence_dir='./blossom-public/blossompy/src/sequences')
        self.bl.connect()  # safe init and connects to blossom and puts blossom in reset position
        self.bl.load_sequences()
        self.bl.do_sequence("reset")
        logger.info("Blossom Connected & Initialized.")

    def reset(self):
        self.bl.do_sequence("reset")

    def do_random_sequence_from_list(self, seq_list, delay_time=0):
        random.shuffle(seq_list)
        time.sleep(delay_time)
        logger.info(f"Blossom playing sequence {seq_list[0]}")
        self.bl.do_sequence(seq_list[0])

    def do_idle_sequence(self, delay_time=0):
        idle_sequences = ["breathing/exhale", "breathing/inhale", "fear/fear_startled", "happy/happy_lookingup",
                          "sad/sad_downcast"]
        self.do_random_sequence_from_list(idle_sequences, delay_time)

    def do_start_sequence(self, delay_time=0):
        self.do_random_sequence_from_list(config["Blossom"]["sequence_list"]["start"], delay_time)

    def do_prompt_sequence(self, delay_time=0):
        self.do_random_sequence_from_list(config["Blossom"]["sequence_list"]["prompt"], delay_time)

    def do_end_sequence(self, delay_time=0):
        self.do_random_sequence_from_list(config["Blossom"]["sequence_list"]["end"], delay_time)

    def do_sequence(self, seq="reset", delay_time=0):
        logger.info(f"Blossom start playing sequence {seq} with {delay_time} s of delay.")
        time.sleep(delay_time)
        logger.info(f"Blossom playing sequence {seq}")
        self.bl.do_sequence(seq)

    # def do_sequence(self, seq="reset"):
    #     self.bl.do_sequence(seq)


bl = Blossom(sequence_dir='./blossom-public/blossompy/src/sequences')
bl.connect()  # safe init and connects to blossom and puts blossom in reset position
bl.load_sequences()
while True:
    sequence_id = input("Input sequence: ")
    bl.do_sequence(sequence_id)
bl.do_sequence("reset")
