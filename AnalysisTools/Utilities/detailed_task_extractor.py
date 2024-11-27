# This file reads in detailed_timestamps.txt and slice raw videos to response
# See detailed_timestamps.txt for example.

import re

from datetime import timedelta


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

        time_str = match.group(2)
        time_str = time_str.replace("'", "")
        time_tuples = re.findall(r"\((\d{2}:\d{2}), (\d{2}:\d{2})\)", time_str)
        time_tuples = [(start, end) for start, end in time_tuples]
        print(f"{identifier}: ")
        flag = True
        # total_response_duration = 0
        total_response_duration = None
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
            else:
                print(f"{time_tuple}, Is Prompt: {flag}")
            flag = not flag
        print(total_response_duration)
        print(int(total_response_duration.total_seconds()))
