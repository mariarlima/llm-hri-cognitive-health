import re
import argparse
import subprocess
from datetime import timedelta
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.editor import concatenate_videoclips, ColorClip


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


def parse_time(time_str):
    """Parse time string in the format 'MM:SS' and return a timedelta object."""
    minutes, seconds = map(int, time_str.split(':'))
    return timedelta(minutes=minutes, seconds=seconds)


def calculate_duration(start_time, end_time):
    """Calculate the duration between two timestamps."""
    return end_time - start_time


with open('detailed_timestamps.txt', 'r') as file:
    lines = file.readlines()

for line in lines:
    match = re.match(r"(P\d{2} S\d) '(\[.*\])'", line)

    if match:
        identifier = match.group(1)

        filename = identifier.replace(" ", "_") + "_T1.mov"
        output_filename = identifier.replace(" ", "_") + "_T1_response_only.mov"
        original_codec = get_video_info(filename)

        time_str = match.group(2)
        time_str = time_str.replace("'", "")
        time_tuples = re.findall(r"\((\d{2}:\d{2}), (\d{2}:\d{2})\)", time_str)
        time_tuples = [(start, end) for start, end in time_tuples]
        print(f"{identifier}: ")
        flag = True
        # total_response_duration = 0
        total_response_duration = None
        video = VideoFileClip(filename)
        response_clips = []
        for time_tuple in time_tuples:
            if not flag:
                start_time = parse_time(time_tuple[0])
                end_time = parse_time(time_tuple[1])
                duration = calculate_duration(start_time, end_time)
                if total_response_duration is None:
                    total_response_duration = duration
                else:
                    total_response_duration += duration
                print(f"{time_tuple}, Is Prompt: {flag}, duration: {duration}")
                response_clips.append(video.subclip(start_time.total_seconds(), end_time.total_seconds()))
            else:
                print(f"{time_tuple}, Is Prompt: {flag}")
            flag = not flag
        print(total_response_duration)
        print(int(total_response_duration.total_seconds()))
        final_video = concatenate_videoclips(response_clips)
        final_video.write_videofile(output_filename, codec=original_codec["video_codec"],
                                    audio_codec=original_codec["audio_codec"])
