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
#
#
# def extract_timestamp(filename):
#     timestamp_str = os.path.basename(filename)
#     timestamp_str, _ = os.path.splitext(timestamp_str)
#     return datetime.datetime.strptime(timestamp_str, '%Y-%m-%dT%H-%M-%S.%f')
#
#
# def get_latest_save_filename(saves_dir="./log"):
#     import os
#     import glob
#     list_of_files = glob.glob(f"{saves_dir}/*.log")
#     # Sort the list of files based on the timestamp in their names
#     list_of_files.sort(key=extract_timestamp)
#
#     # The last file in the list is the one with the latest timestamp
#     latest_filename = list_of_files[-1]
#     return latest_filename
#
# print(get_latest_save_filename())

"""Getting Started Example for Python 2.7+/3.3+"""
from boto3 import Session
from botocore.exceptions import BotoCoreError, ClientError
from contextlib import closing
import os
import sys
import subprocess
from tempfile import gettempdir

# Create a client using the credentials and region defined in the [default]
# section of the AWS credentials file (~/.aws/credentials).
session = Session(profile_name="default")
polly = session.client("polly")
text = """¡Genial! Vamos a jugar un divertido juego de contar historias. Mira la imagen en la pantalla y dime qué ves. 
Puedes describir los objetos, personas o acciones que están sucediendo. ¡Cuantos más detalles, mejor! Comienza cuando 
estés listo. Te daré pistas si las necesitas."""

try:
    # Request speech synthesis
    response = polly.synthesize_speech(Text=text, OutputFormat="mp3",
                                       VoiceId="Penelope")
except (BotoCoreError, ClientError) as error:
    # The service returned an error, exit gracefully
    print(error)
    sys.exit(-1)

# Access the audio stream from the response
if "AudioStream" in response:
    # Note: Closing the stream is important because the service throttles on the
    # number of parallel connections. Here we are using contextlib.closing to
    # ensure the close method of the stream object will be called automatically
    # at the end of the with statement's scope.
    with closing(response["AudioStream"]) as stream:
        output = os.path.join(gettempdir(), "speech.mp3")

        try:
            # Open a file for writing the output as a binary stream
            with open(output, "wb") as file:
                file.write(stream.read())
        except IOError as error:
            # Could not write to file, exit gracefully
            print(error)
            sys.exit(-1)

else:
    # The response didn't contain audio data, exit gracefully
    print("Could not stream audio")
    sys.exit(-1)

# Play the audio using the platform's default player
if sys.platform == "win32":
    os.startfile(output)
else:
    # The following works on macOS and Linux. (Darwin = mac, xdg-open = linux).
    opener = "open" if sys.platform == "darwin" else "xdg-open"
    subprocess.call([opener, output])
