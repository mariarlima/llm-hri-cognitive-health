import re
from datetime import timedelta


def parse_time(time_str):
    """Parse time string in the format 'MM:SS' and return a timedelta object."""
    minutes, seconds = map(int, time_str.split(':'))
    return timedelta(minutes=minutes, seconds=seconds)


def calculate_duration(start_time, end_time):
    """Calculate the duration between two timestamps."""
    return end_time - start_time


def extract_info_and_calculate_duration(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    for line in lines:
        # Extract the "Pxx Sx" part
        match = re.search(r'P\d{2}_S\d', line)
        if not match:
            continue

        video_name = match.group(0).replace('_', ' ')  # Format it as "Pxx Sx"

        # Extract the timestamps
        timestamps = re.findall(r'\((\d{2}:\d{2}),(\d{2}:\d{2})\)', line)

        if len(timestamps) == 2:
            start1, end1 = timestamps[0]
            start2, end2 = timestamps[1]

            # Calculate durations
            duration1 = calculate_duration(parse_time(start1), parse_time(end1))
            duration2 = calculate_duration(parse_time(start2), parse_time(end2))
            total_duration = duration1 + duration2

            # Convert timedelta to minutes and seconds
            duration1_seconds = int(duration1.total_seconds())
            duration2_seconds = int(duration2.total_seconds())
            total_seconds = int(total_duration.total_seconds())

            print(
                f"{video_name}: Duration1 = {duration1_seconds} seconds, Duration2 = {duration2_seconds} seconds, Total Duration = {total_seconds} seconds")


file_path = 'video_slicing.sh'
extract_info_and_calculate_duration(file_path)
