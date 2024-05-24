from DevTools.audio_latency_test import get_audio_length, read_mp3_as_bytes
from blossom_interaction import BlossomInterface
import sounddevice as sd
import soundfile as sf
from unrealspeech import UnrealSpeechAPI, play, save
from blossom_interaction import BlossomInterface
import os
import datetime
import threading

# # Example usage
# # os.chdir("../../")
# print(os.getcwd())
# bl = BlossomInterface()
# input()
# file_path_ = './voiceover1.mp3'
# audio_bytes_ = read_mp3_as_bytes(file_path_)
# duration = get_audio_length(audio_bytes_)
# print(f"Audio length: {duration} seconds")
# # sd.play(*sf.read(BytesIO(audio_bytes_)))
# bl_thread = threading.Thread(target=bl.do_sequence, args=("grand/grand1", 1))
# bl_thread.start()
# # bl.do_prompt_sequence()
# play(audio_bytes_)
# # sd.wait()
# bl_thread.join()


def extract_timestamp(filename):
    timestamp_str = os.path.basename(filename)
    timestamp_str, _ = os.path.splitext(timestamp_str)
    return datetime.datetime.strptime(timestamp_str, '%Y-%m-%dT%H-%M-%S.%f')


def get_latest_save_filename(saves_dir="./log"):
    import os
    import glob
    list_of_files = glob.glob(f"{saves_dir}/*.log")
    # Sort the list of files based on the timestamp in their names
    list_of_files.sort(key=extract_timestamp)

    # The last file in the list is the one with the latest timestamp
    latest_filename = list_of_files[-1]
    return latest_filename

print(get_latest_save_filename())