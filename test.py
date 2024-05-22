from DevTools.audio_latency_test import get_audio_length, read_mp3_as_bytes
from blossom_interaction import BlossomInterface
import sounddevice as sd
import soundfile as sf
from unrealspeech import UnrealSpeechAPI, play, save
from blossom_interaction import BlossomInterface
import os
import threading

# Example usage
# os.chdir("../../")
print(os.getcwd())
bl = BlossomInterface()
input()
file_path_ = './voiceover1.mp3'
audio_bytes_ = read_mp3_as_bytes(file_path_)
duration = get_audio_length(audio_bytes_)
print(f"Audio length: {duration} seconds")
# sd.play(*sf.read(BytesIO(audio_bytes_)))
bl_thread = threading.Thread(target=bl.do_sequence, args=("grand/grand1", 1))
bl_thread.start()
# bl.do_prompt_sequence()
play(audio_bytes_)
# sd.wait()
bl_thread.join()
