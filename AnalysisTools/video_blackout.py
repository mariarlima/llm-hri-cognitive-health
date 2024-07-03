from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.editor import concatenate_videoclips
import argparse
import ast
import os
import subprocess
import re


def convert_to_seconds(time_str):
    minutes, seconds = map(int, time_str.split(':'))
    return minutes * 60 + seconds


def get_video_info(video_path):
    # Run ffmpeg command to get video information
    result = subprocess.run(['ffmpeg', '-i', video_path], stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    output = result.stderr.decode('utf-8')  # ffmpeg outputs to stderr by default

    # Find codec information using regular expressions
    video_codec = re.search(r'Video: (\w+)', output)
    audio_codec = re.search(r'Audio: (\w+)', output)

    return {
        'video_codec': video_codec.group(1) if video_codec else 'Unknown',
        'audio_codec': audio_codec.group(1) if audio_codec else 'Unknown'
    }


video_file = "./P02_S3_T1_2.mp4"
# subclip_tuples = [(57.980, 128.940), (144.860, 180.300), (210.540, 247.860), (277.680, 301.420)]
subclip_tuples = [(57.980, 128.940), (128.940, 144.860), (144.860, 180.300), (180.300, 210.540), (210.540, 247.860),
                  (247.860, 277.680), (277.680, 301.420)]

video = VideoFileClip(video_file)

# # Define the start and end times for multiple slices
# slices = [(10, 20), (30, 40), (50, 60)]

# Create a list of video clips
blackout_flag = False
clips = []  # [video.subclip(start, end) for start, end in subclip_tuple]
for start, end in subclip_tuples:
    if not blackout_flag:
        clips.append(video.subclip(start, end))
    else:
        clips.append(video.subclip(start, end).without_audio())
    blackout_flag = not blackout_flag

original_codec = get_video_info(video_file)

output_filename = os.path.join("./", f"{"P02_S3_T1"}_blackout_{".mp4"}")
final_video = concatenate_videoclips(clips)
final_video.write_videofile(output_filename, codec=original_codec["video_codec"], audio_codec=original_codec["audio_codec"])
print("Done")
