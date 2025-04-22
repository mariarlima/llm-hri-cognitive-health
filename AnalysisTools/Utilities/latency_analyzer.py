import re
from datetime import datetime

# Function to extract timestamps from a string
def extract_timestamps(text):
    pattern = r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}'
    return re.findall(pattern, text)

# Function to calculate the time interval between two timestamps in milliseconds
def calculate_interval(timestamp1, timestamp2):
    time_format = '%Y-%m-%d %H:%M:%S,%f'
    dt1 = datetime.strptime(timestamp1, time_format)
    dt2 = datetime.strptime(timestamp2, time_format)
    interval = (dt2 - dt1).total_seconds() * 1000  # Convert to milliseconds
    return interval

def read_log_file(file_path):
    with open(file_path, 'r') as file:
        for line in file:
            yield line.strip()

# # Example usage
# text = "Some log text with timestamps 2024-07-05 15:48:57,359 and 2024-07-05 15:49:00,123"
# timestamps = extract_timestamps(text)
# if len(timestamps) >= 2:
#     interval = calculate_interval(timestamps[0], timestamps[1])
#     print(f"Time interval: {interval} milliseconds")
# else:
#     print("Not enough timestamps found")

if __name__ == "__main__":
    # Read the log file
    log_file_path = "log.txt"
    log_lines = read_log_file(log_file_path)

    # Initialize variables
    start_time = None
    end_time = None
    total_interval = 0
    start_found = False
    delay_intervals = []

    # Process each line in the log file
    for line in log_lines:
        if "Transcribing..." in line:
            start_found = True
            print(f"Delay start: {line}")
            start_time = extract_timestamps(line)
        if start_found and "Sending data to server:" in line:
            start_found = False
            print(f"Delay end: {line}")
            end_time = extract_timestamps(line)
            interval = calculate_interval(start_time[0], end_time[0])
            print(f"Delay interval: {interval} milliseconds")
            delay_intervals.append(interval)
        continue
