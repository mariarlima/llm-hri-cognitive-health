import random
import sys

sys.path.append("./blossom-public")
from blossompy import Blossom


class BlossomInterface:
    def __init__(self):
        self.bl = Blossom(sequence_dir='./blossom-public/blossompy/src/sequences')
        self.bl.connect()  # safe init and connects to blossom and puts blossom in reset position
        self.bl.load_sequences()
        self.bl.do_sequence("reset")

    def reset(self):
        self.bl.do_sequence("reset")

    def do_idle_sequence(self):
        idle_sequences = ["breathing/exhale", "breathing/inhale", "fear/fear_startled", "happy/happy_lookingup",
                          "sad/sad_downcast"]
        random.shuffle(idle_sequences)
        self.bl.do_sequence(idle_sequences[0])

    def do_sequence(self, seq="reset"):
        self.bl.do_sequence(seq)


# bl = Blossom(sequence_dir='./blossom-public/blossompy/src/sequences')
# bl.connect()  # safe init and connects to blossom and puts blossom in reset position
# bl.load_sequences()
# while True:
#     sequence_id = input("Input sequence: ")
#     bl.do_sequence("grand/grand1")
#     bl.do_sequence("yes")
#     bl.do_sequence("grand/grand2")
#     bl.do_sequence(sequence_id)
# bl.do_sequence("reset")
