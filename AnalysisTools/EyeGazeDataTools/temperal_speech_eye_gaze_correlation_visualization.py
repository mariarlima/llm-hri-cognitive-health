import os
import math
import json
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable
from matplotlib.colors import LinearSegmentedColormap
from scipy.ndimage import gaussian_filter
from utils import plotting


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


def generate_correlated_visualization(data_path, transcription_path, timestamps_str, title="Correlation Visualization",
                                      figure_path="./figures/", time_offset=0.0,
                                      figsize=(5, 4), dpi=600):
    cookie_image_path = "./images/The-Cookie-Theft-Picture-from-the-Boston-Diagnostic-Aphasia-Examination-For-the-PD-task.png"
    picnic_image_path = "./images/picnic.png"
    height = 900
    width = 1600
    max_char_per_line = 100
    # time_offset = 35.0
    duration_threshold = 0.2
    line_height = 0.035
    char_offset = 0.01
    max_duration = 0.0
    filename_with_extension = os.path.basename(data_path)
    base_name, _ = os.path.splitext(filename_with_extension)

    # Prepare timestamps
    subclip_tuples = parse_input_timestamp(timestamps_str)
    timestamps_set = set()

    for start, end in subclip_tuples:
        timestamps_set.add(convert_to_seconds(start))
        timestamps_set.add(convert_to_seconds(end))

    timestamps = list(timestamps_set)
    timestamps.sort()
    blackout_flag = True
    timestamps.pop(0)

    # Prepare transcription data
    transcription_raw_data = None
    with open(transcription_path, 'r') as f:
        transcription_raw_data = json.load(f)

    transcription_data = [[], []]
    for segment in transcription_raw_data["segments"]:
        for word in segment["words"]:
            if word["start"] > timestamps[0]:
                timestamps.pop(0)
                blackout_flag = not blackout_flag
                print(timestamps)
                print(blackout_flag)
                print(transcription_data)
            if not blackout_flag:
                transcription_data[0].append(word["word"])
                transcription_data[1].append(word["start"])
            max_duration = max(max_duration, word["end"])

    processed_line_data = [[], []]
    # processed_transcription_data = [[[" "] * max_char_per_line, [0.0] * max_char_per_line]]
    processed_transcription_data = []
    for i in range(0, len(transcription_data[0])):
        if len(processed_line_data[:-1][0]) + len(transcription_data[0][i]) < max_char_per_line:
            for j in range(0, len(transcription_data[0][i])):
                processed_line_data[0].append(transcription_data[0][i][j])
                processed_line_data[1].append(transcription_data[1][i])
            # processed_line_data[0].append(" ")
            # processed_line_data[1].append(transcription_data[1][i])
        else:
            processed_transcription_data.append(processed_line_data)
            processed_line_data = [[], []]
            for j in range(0, len(transcription_data[0][i])):
                processed_line_data[0].append(transcription_data[0][i][j])
                processed_line_data[1].append(transcription_data[1][i])
            # processed_line_data[0].append(" ")
            # processed_line_data[1].append(transcription_data[1][i])
    processed_transcription_data.append(processed_line_data)

    max_duration += 0.5

    # Prepare eye gaze data
    df = pd.read_csv(data_path)

    if df["MEDIA_NAME"][0] == "Cognitive Picture Description Task":
        background_image_path = cookie_image_path
    else:
        background_image_path = picnic_image_path
    # print(pandas_data.head())
    # Create a blank image with 16:9 aspect ratio
    filtered_pts = df[
        (df['FPOGX'] >= 0.0) & (df['FPOGX'] <= 1.0) & (df['FPOGY'] >= 0.0) & (df['FPOGY'] <= 1.0) & (
                df['FPOGV'] == 1) & (df['FPOGD'] > duration_threshold) & (
                df.iloc[:, 3] + time_offset <= max_duration) & (
                df.iloc[:, 3] + time_offset >= 0)]

    # print(filtered_pts[["FPOGX", "FPOGY"]].describe())

    # points = filtered_pts[['FPOGX', 'FPOGY', 'TIME(2024/06/13 11:07:59.703)', 'FPOGD']].values
    points = filtered_pts.iloc[:, [5, 6, 3, 8]].values
    # print(points)
    # Scale points to the image dimensions
    points[:,0] *= width
    points[:, 1] *= height
    points[:, 2] += time_offset
    points[:, 3] *= 15
    # print(points)
    # (196, 199, 243), (23, 33, 33)
    # custom_cmap = LinearSegmentedColormap.from_list('mycmap', ['lightsteelblue', 'midnightblue'], N=256)
    # custom_cmap = sns.color_palette("crest", as_cmap=True)
    custom_cmap = "winter"  # cool, winter
    norm = Normalize(vmin=0, vmax=max(points[:, 2]))
    sm = ScalarMappable(cmap=custom_cmap, norm=norm)

    plt.figure(figsize=(max_char_per_line * 0.1 + 1, (
            len(processed_transcription_data) * 0.2)))
    plt.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05)

    for i in range(0, len(processed_transcription_data)):
        line = processed_transcription_data[i]
        for j in range(0, len(line[0])):
            char = line[0][j]
            color = sm.to_rgba(line[1][j])
            if line[1][j] < time_offset:
                color = "red"
            x_offset = j * (1.0 / len(line[0]))
            if len(line[0]) / max_char_per_line < 0.8:
                x_offset = j * (1.0 / max_char_per_line)
            plt.text(x_offset, i * (1.0 / len(processed_transcription_data)), char, color=color,
                     fontsize=10,
                     ha='center',
                     va='center')
    plt.axis('off')
    plt.gca().invert_yaxis()
    # Add background image
    # Step 1: Read the image
    background_image = plt.imread(background_image_path)

    # Step 2: Calculate aspect ratios
    plot_aspect_ratio = height / width
    image_aspect_ratio = background_image.shape[0] / background_image.shape[1]

    # Step 3: Calculate padding
    if plot_aspect_ratio != image_aspect_ratio:
        if plot_aspect_ratio > image_aspect_ratio:
            # The image is too wide, pad top and bottom
            pad_height = int(((background_image.shape[1] * plot_aspect_ratio) - background_image.shape[0]) / 2)
            padding = ((pad_height, pad_height), (0,0), (0,0))
        else:
            # The image is too tall, pad left and right
            pad_width = int(((background_image.shape[0] / plot_aspect_ratio) - background_image.shape[1]) / 2)
            padding = ((0,0), (pad_width, pad_width), (0,0))

        # Step 4: Apply padding
        background_image_padded = np.pad(background_image, padding, mode='constant', constant_values=255)
    else:
        background_image_padded = background_image

    # # Create a figure with the background image
    with plotting.paper_theme():
        plt.figure(figsize=figsize)
        plt.imshow(background_image_padded, extent=[0, width, height,0])
        scatter = plt.scatter(points[:,0], points[:, 1], c=points[:, 2], cmap=custom_cmap, s=points[:, 3], alpha=0.7)
        # plt.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05)
        plt.colorbar(shrink=0.5, pad=0.01)
        plt.axis('off')
        plt.title(title, fontsize=10)

    plt.tight_layout()
    figs = [plt.figure(n) for n in plt.get_fignums()]
    for i, fig in enumerate(figs):
        suffix = "_eye_gaze"
        if i == 0:
            suffix = "_text"
        fig.savefig(f"{figure_path}{filename_with_extension.replace("_fixations.csv", "")}{suffix}.png", format='png', dpi=dpi)
    # plt.show()
    plt.close('all')


generate_correlated_visualization("./data/P02_S1_fixations.csv", "./data/P02_S1_T1.json",
                                  timestamps_str='[(00:00,00:24), (00:24,02:00), (02:00,02:08), (02:08,02:35), (02:35,02:42), (02:42,03:21), (03:21,03:28), (03:28,03:51), (03:51,04:00), (04:00,04:44), (04:44,04:51)]',
                                  time_offset=2)
generate_correlated_visualization("./data/P02_S2_fixations.csv", "./data/P02_S2_T1.json",
                                  timestamps_str='[(00:00,01:09), (01:09,01:16), (01:16,01:26), (01:26,04:02), (04:02,04:30)]',
                                  time_offset=47)
generate_correlated_visualization("./data/P02_S3_fixations.csv", "./data/P02_S3_T1.json",
                                  timestamps_str='[00:00,00:57), (00:57,02:09), (02:09,02:24), (02:24,03:10), (03:10,03:26), (03:26,04:07), (04:07,04:37), (04:37,05:01), (05:01,05:22)]',
                                  time_offset=35)
generate_correlated_visualization("./data/P02_S4_fixations.csv", "./data/P02_S4_T1.json",
                                  timestamps_str='[(00:00,00:43), (00:43,01:55), (01:55,02:14), (02:14,02:39), (02:39,03:52), (03:52,04:21), (04:21,05:30), (05:30,05:38)]',
                                  time_offset=22)
generate_correlated_visualization("./data/P02_S5 # Partial_fixations.csv", "./data/P02_S5_T1.json",
                                  timestamps_str='[(00:00,00:15), (00:15,02:37), (02:37,02:45), (02:45,03:22), (03:22,03:37), (03:37,03:56), (03:56,04:06), (04:06,04:37), (04:37,04:46)]',
                                  time_offset=3)

generate_correlated_visualization("./data/P07_S1_fixations.csv", "./data/P07_S1_T1.json",
                                  timestamps_str='[(00:00,00:33), (00:33,00:57), (00:57,01:07), (01:07,01:17), (01:17,01:23), (01:23,01:32), (01:32,01:34), (01:34,01:42), (01:42,01:46), (01:46,01:57), (01:57,02:07), (02:07,02:34), (02:34,02:50), (02:50,03:13), (03:13,03:23)]',
                                  time_offset=2)
generate_correlated_visualization("./data/P07_S2_fixations.csv", "./data/P07_S2_T1.json",
                                  timestamps_str='[(00:00,00:35), (00:35,00:40), (00:40,00:44), (00:44,00:58), (00:58,01:11), (01:11,01:32), (01:32,01:48), (01:48,02:25), (02:25,02:57), (02:57,03:13), (03:13,03:35), (03:35,03:48), (03:48,04:15), (04:15,04:41), (04:41,05:01), (05:01,05:43), (05:43,05:53)]',
                                  time_offset=14)
generate_correlated_visualization("./data/P07_S3_fixations.csv", "./data/P07_S3_T1.json",
                                  timestamps_str='[(00:00,01:29), (01:29,01:38), (01:38,01:50), (01:50,02:14), (02:14,02:48), (02:48,02:52), (02:52,03:00), (03:00,03:26), (03:26,03:42), (03:42,04:06), (04:06,04:26), (04:26,04:53), (04:53,05:14), (05:14,05:34), (05:34,05:42)]',
                                  time_offset=66)
generate_correlated_visualization("./data/P07_S4_fixations.csv", "./data/P07_S4_T1.json",
                                  timestamps_str='[(00:00,00:44), (00:44,02:18), (02:18,02:41), (02:41,02:56), (02:56,03:11), (03:11,03:22), (03:22,03:51), (03:51,05:09), (05:09,05:24)]',
                                  time_offset=30)
generate_correlated_visualization("./data/P07_S5_fixations.csv", "./data/P07_S5_T1.json",
                                  timestamps_str='[(00:00,00:14), (00:14,00:58), (00:58,01:08), (01:08,01:20), (01:20,01:29), (01:29,01:49), (01:49,01:53), (01:53,01:55), (01:55,02:02), (02:02,02:24), (02:24,02:38), (02:38,03:14), (03:14,03:24)]',
                                  time_offset=5)

generate_correlated_visualization("./data/P14_S1_fixations.csv", "./data/P14_S1_T1.json",
                                  timestamps_str='[(00:00,00:36), (00:36,00:53), (00:53,01:05), (01:05,01:15), (01:15,01:26), (01:26,01:33), (01:33,01:35), (01:35,01:36), (01:36,01:41), (01:41,01:47), (01:47,02:02), (02:02,02:24), (02:24,02:30)]',
                                  time_offset=2)
generate_correlated_visualization("./data/P14_S2_fixations.csv", "./data/P14_S2_T1.json",
                                  timestamps_str='[(00:00,01:15), (01:15,01:15), (01:15,01:25), (01:25,01:48), (01:48,01:58), (01:58,02:26), (02:26,02:49), (02:49,03:10), (03:10,03:31), (03:31,03:47), (03:47,04:02)]',
                                  time_offset=14)
generate_correlated_visualization("./data/P14_S3_fixations.csv", "./data/P14_S3_T1.json",
                                  timestamps_str='[(00:00,00:59), (00:59,02:32), (02:32,02:36), (02:36,02:36), (02:36,02:46), (02:46,03:38), (03:38,04:06)]',
                                  time_offset=66)
generate_correlated_visualization("./data/P14_S4 # Double Check_fixations.csv", "./data/P14_S4_T1.json",
                                  timestamps_str='[(00:00,00:49), (00:49,01:57), (01:57,01:59), (01:59,01:59), (01:59,02:06), (02:06,02:06), (02:06,02:11), (02:11,03:14), (03:14,03:30), (03:30,03:52), (03:52,04:10)]',
                                  time_offset=30)
generate_correlated_visualization("./data/P14_S5 # Double Check_fixations.csv", "./data/P14_S5_T1.json",
                                  timestamps_str='[(00:00,00:20), (00:20,01:33), (01:33,01:40), (01:40,01:49), (01:49,01:59), (01:59,02:33), (02:33,02:43)]',
                                  time_offset=5)
