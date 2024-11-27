import datetime
import json
import os

from pydub import AudioSegment
from io import BytesIO
import requests

save_dir = "../Config/save"
final_save_dir = "../Config/FinalSaves"

def read_mp3_as_bytes(file_path):
    with open(file_path, 'rb') as file:
        audio_bytes = file.read()
    return audio_bytes


def read_mp3_as_bytes_url(url):
    response = requests.get(url)
    response.raise_for_status()  # Ensure the request was successful
    audio_bytes = response.content
    return audio_bytes


def get_audio_length(audio_bytes):
    audio = AudioSegment.from_file(BytesIO(audio_bytes), format="mp3")
    duration_in_milliseconds = len(audio)
    duration_in_seconds = duration_in_milliseconds / 1000
    return duration_in_seconds


def extract_timestamp(filename):
    timestamp_str = os.path.basename(filename)
    timestamp_str, _ = os.path.splitext(timestamp_str)
    return datetime.datetime.strptime(timestamp_str, '%Y-%m-%dT%H-%M-%S.%f')


def get_latest_save_filename(saves_dir=save_dir):
    import os
    import glob
    list_of_files = glob.glob(f"{saves_dir}/*.json")
    # Sort the list of files based on the timestamp in their names
    list_of_files.sort(key=extract_timestamp)

    # The last file in the list is the one with the latest timestamp
    latest_filename = list_of_files[-1]
    return latest_filename


def create_save(save_data):
    save_filename = f'{save_dir}/{datetime.datetime.now().isoformat().replace(":", "-")}.json'
    with open(save_filename, 'w') as save_file:
        json.dump(save_data, save_file)
    return save_filename


def create_final_save(save_data):
    save_filename = f'{final_save_dir}/{datetime.datetime.now().isoformat().replace(":", "-")}.json'
    with open(save_filename, 'w') as save_file:
        json.dump(save_data, save_file)
    return save_filename


def load_save(save_filename):
    with open(save_filename, 'r') as save_file:
        save_data = json.load(save_file)
    return save_data


def load_latest_save():
    latest_save_filename = get_latest_save_filename()
    return load_save(latest_save_filename)


def get_integer_input(prompt):
    try:
        return int(input(prompt))
    except ValueError:
        print("NAN input detected. Return input as 0.")
        return 0
