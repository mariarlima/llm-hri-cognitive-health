# Copy this file to video directory
import os
from moviepy.editor import VideoFileClip

# Define the video file extensions to look for
video_extensions = ['.mp4', '.mkv', '.avi', '.mov', '.flv']


# Function to extract audio from a video file
def extract_audio(video_path, audio_path):
    with VideoFileClip(video_path) as video:
        audio = video.audio
        audio.write_audiofile(audio_path)


# Get the list of all files in the current directory
files_in_directory = os.listdir('.')

# Process each file
for file_name in files_in_directory:
    # Check if the file has a video extension
    if any(file_name.endswith(ext) for ext in video_extensions):
        # Define the audio file name (same as video but with .mp3 extension)
        audio_file_name = os.path.splitext(file_name)[0] + '.mp3'
        # Extract the audio
        extract_audio(file_name, audio_file_name)
        print(f"Extracted audio from {file_name} to {audio_file_name}")
