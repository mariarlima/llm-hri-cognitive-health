from moviepy.video.io.VideoFileClip import VideoFileClip
import argparse
import ast
import os
import subprocess
import re


def parse_input_timestamp(input_str):
    # Remove the outer brackets
    input_str = input_str[1:-1]

    # Split the string by '), (' to get a list of tuples as strings
    tuple_strs = input_str.split('), (')

    # For each tuple string, remove the inner brackets and split by ',' to get the start and end times as strings
    tuples = [tuple_str.replace('(', '').replace(')', '').split(', ') for tuple_str in tuple_strs]
    tuples = [item[0].split(',') for item in tuples]
    print(f"Tuple: {tuples}")

    # Split each time string by ':' to get the hours and minutes as strings, and convert them to integers
    tuples = [(start, end) for start, end in tuples]

    return tuples


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


# Create the parser
parser = argparse.ArgumentParser(description="Video Slicer Tool CLI")

# Add the arguments
parser.add_argument('-f', '--file', type=str, required=True, help="Input video file.")
# parser.add_argument('-o', '--output', type=str, required=True, help="The output file")
parser.add_argument('-s', '--subclip', type=str, required=False,
                    help="List of subclip tuples. In the order of task1, task2, interview", default="[]")

# Parse the arguments
args = parser.parse_args()

# input_timestamps = re.sub(r'\b0+(\d)', r'\1', args.subclip)
subclip_tuple = parse_input_timestamp(args.subclip)  # ast.literal_eval(input_timestamps)

dir_name = os.path.dirname(args.file)
base_name = os.path.basename(args.file)
name, ext = os.path.splitext(base_name)
video = VideoFileClip(args.file)

# # Define the start and end times for multiple slices
# slices = [(10, 20), (30, 40), (50, 60)]

# Create a list of video clips
clips = []  # [video.subclip(start, end) for start, end in subclip_tuple]
for start, end in subclip_tuple:
    print(f"Subclip: {start} - {end}")
    start_second = convert_to_seconds(start)
    end_second = convert_to_seconds(end)
    print(f"Convert to seconds: {start_second} - {end_second}")
    clips.append(video.subclip(start_second, end_second))

clips_subfix = ["T1", "T2", "interview"]

original_codec = get_video_info(args.file)

index = 0
for clip in clips:
    if index >= len(clips_subfix) - 1:
        clips_subfix.append(f"unmarked_clip_{index}")
    output_filename = os.path.join(dir_name, f"{name}_{clips_subfix[index]}{ext}")
    print(f"Saving sliced video {output_filename} duration: {clip.duration}")
    clip.write_videofile(output_filename, codec=original_codec["video_codec"],
                         audio_codec=original_codec["audio_codec"],
                         ffmpeg_params=["-movflags", "faststart"])
    print("Done")
    index += 1
