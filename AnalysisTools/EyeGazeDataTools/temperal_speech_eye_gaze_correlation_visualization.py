import math
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable
from matplotlib.colors import LinearSegmentedColormap
from scipy.ndimage import gaussian_filter
from utils import plotting


def generate_correlated_visualization(data_path, transcription_path, title="Correlation Visualization",
                                      figure_path="./figure.png",
                                      figsize=(5, 4), dpi=600):
    cookie_image_path = "./images/The-Cookie-Theft-Picture-from-the-Boston-Diagnostic-Aphasia-Examination-For-the-PD-task.png"
    picnic_image_path = "./images/picnic.png"
    height = 900
    width = 1600
    max_char_per_line = 100
    time_offset = 35.0
    duration_threshold = 0.5
    line_height = 0.035
    char_offset = 0.01
    # data_path = "./data/P23_S1_all_gaze.csv"

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
                    df['FPOGV'] == 1) & (df['FPOGD'] > duration_threshold)]

    # print(filtered_pts[["FPOGX", "FPOGY"]].describe())

    points = filtered_pts[['FPOGX', 'FPOGY', 'TIME(2024/06/13 11:07:59.703)', 'FPOGD']].values
    # print(points)
    # Scale points to the image dimensions
    points[:, 0] *= width
    points[:, 1] *= height
    points[:, 2] += time_offset
    points[:, 3] *= 50
    # print(points)
    # (196, 199, 243), (23, 33, 33)
    custom_cmap = LinearSegmentedColormap.from_list('mycmap', ['blue', 'orange'], N=256)
    norm = Normalize(vmin=0, vmax=max(points[:, 2]))
    sm = ScalarMappable(cmap=custom_cmap, norm=norm)

    # Prepare transcription data
    transcription_raw_data = None
    with open(transcription_path, 'r') as f:
        transcription_raw_data = json.load(f)

    transcription_data = [[], []]
    for segment in transcription_raw_data["segments"]:
        for word in segment["words"]:
            transcription_data[0].append(word["word"])
            transcription_data[1].append(word["start"])

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

    plt.figure(figsize=(max_char_per_line * 0.1 + 1, (
            len(processed_transcription_data) * 0.2)))
    plt.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05)

    for i in range(0, len(processed_transcription_data)):
        line = processed_transcription_data[i]
        for j in range(0, len(line[0])):
            char = line[0][j]
            color = sm.to_rgba(line[1][j])
            if line[1][j] < time_offset:
                color = "black"
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
            padding = ((pad_height, pad_height), (0, 0), (0, 0))
        else:
            # The image is too tall, pad left and right
            pad_width = int(((background_image.shape[0] / plot_aspect_ratio) - background_image.shape[1]) / 2)
            padding = ((0, 0), (pad_width, pad_width), (0, 0))

        # Step 4: Apply padding
        background_image_padded = np.pad(background_image, padding, mode='constant', constant_values=255)
    else:
        background_image_padded = background_image

    # # Create a figure with the background image
    with plotting.paper_theme():
        plt.figure(figsize=figsize)
        plt.imshow(background_image_padded, extent=[0, width, height, 0])
        scatter = plt.scatter(points[:, 0], points[:, 1], c=points[:, 2], cmap=custom_cmap, s=points[:, 3], alpha=0.7)
        # plt.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05)
        plt.colorbar(shrink=0.5, pad=0.01)
        plt.axis('off')
        plt.title(title, fontsize=10)

    plt.tight_layout()
    figs = [plt.figure(n) for n in plt.get_fignums()]
    for i, fig in enumerate(figs):
        fig.savefig(f"./figure{i}.png", format='png', dpi=dpi)
    # plt.show()
    plt.close('all')


generate_correlated_visualization("./data/P02_S3_all_gaze.csv", "./data/P02_S3_T1_2.json")
