import random
import sys
import time
import logging
from .config import config

# sys.path.append("./blossom_public")
from .blossom_public.blossompy import Blossom

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
        logger.info(f"Blossom start playing sequence {seq_list[0]} with {delay_time}s of delay.")
        time.sleep(delay_time)
        logger.info(f"Blossom playing sequence {seq_list[0]}")
        self.bl.do_sequence(seq_list[0])

    def do_idle_sequence(self, delay_time=0):
        idle_sequences = ["breathing/exhale", "breathing/inhale", "fear/fear_startled", "happy/happy_lookingup",
                          "sad/sad_downcast"]
        self.do_random_sequence_from_list(idle_sequences, delay_time)

    def do_start_sequence(self, delay_time=0):
        logger.info(f"Tread Target: do_start_sequence, delay_time: {delay_time}")
        self.do_random_sequence_from_list(config["Blossom"]["sequence_list"]["start"], delay_time)

    def do_prompt_sequence(self, delay_time=0):
        logger.info(f"Tread Target: do_prompt_sequence, delay_time: {delay_time}")
        self.do_random_sequence_from_list(config["Blossom"]["sequence_list"]["prompt"], delay_time)

    def do_end_sequence(self, delay_time=0):
        logger.info(f"Tread Target: do_end_sequence, delay_time: {delay_time}")
        self.do_random_sequence_from_list(config["Blossom"]["sequence_list"]["end"], delay_time)

    def do_prompt_sequence_matching(self, delay_time=0, audio_length=0):
        logger.info(
            f"Tread Target: do_prompt_sequence_matching, delay_time: {delay_time}, audio_length: {audio_length}")
        if audio_length >= config["Blossom"]["sequence_length_boundary_list"]["prompt"][-1]:
            self.do_random_sequence_from_list(config["Blossom"]["sequence_list"]["prompt"], delay_time)
        else:
            for i in range(0, len(config["Blossom"]["sequence_length_boundary_list"]["prompt"])):
                if audio_length < config["Blossom"]["sequence_length_boundary_list"]["prompt"][i]:
                    self.do_random_sequence_from_list(config["Blossom"]["sequence_list"]["prompt_timed"][i], delay_time)
                    break

    def do_sequence(self, seq="reset", delay_time=0):
        logger.info(f"Blossom start playing sequence {seq} with {delay_time}s of delay.")
        time.sleep(delay_time)
        logger.info(f"Blossom playing sequence {seq}")
        self.bl.do_sequence(seq)
