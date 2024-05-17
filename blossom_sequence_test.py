import sys

sys.path.append("./blossom-public")
from blossompy import Blossom

bl = Blossom(sequence_dir='./blossom-public/blossompy/src/sequences')
bl.connect()  # safe init and connects to blossom and puts blossom in reset position
bl.load_sequences()
print("++++++++++++++++++ Initialization Complete ++++++++++++++++++")
print("Press c to quit.")
while True:
    sequence_id = input("Input Sequence: ")
    if sequence_id == "c":
        bl.do_sequence("reset")
        exit()
    bl.do_sequence(sequence_id)
