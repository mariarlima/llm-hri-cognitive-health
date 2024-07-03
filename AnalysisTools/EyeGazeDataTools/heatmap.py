import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from scipy.ndimage import gaussian_filter
from utils import plotting


def generate_heatmap(data_path, title="heatmap", figure_path="./figure.png", sigma=20, use_fixation=False,
                     figsize=(5, 4), dpi=600):
    cookie_image_path = "./images/The-Cookie-Theft-Picture-from-the-Boston-Diagnostic-Aphasia-Examination-For-the-PD-task.png"
    picnic_image_path = "./images/picnic.png"

    # data_path = "./data/P23_S1_all_gaze.csv"

    df = pd.read_csv(data_path)

    if df["MEDIA_NAME"][0] == "Cognitive Picture Description Task":
        background_image_path = cookie_image_path
    else:
        background_image_path = picnic_image_path
    # print(pandas_data.head())
    # Create a blank image with 16:9 aspect ratio
    if not use_fixation:
        filtered_pts = df[
            (df['BPOGX'] >= 0.0) & (df['BPOGX'] <= 1.0) & (df['BPOGY'] >= 0.0) & (df['BPOGY'] <= 1.0) & (
                        df['BPOGV'] == 1)]
    else:
        filtered_pts = df[
            (df['FPOGX'] >= 0.0) & (df['FPOGX'] <= 1.0) & (df['FPOGY'] >= 0.0) & (df['FPOGY'] <= 1.0) & (
                    df['FPOGV'] == 1) & (df['FPOGD'] > 0.2)]
    # print(filtered_pts[["BPOGX", "BPOGY"]].describe())
    height = 900
    width = 1600
    heatmap = np.zeros((height, width))
    if not use_fixation:
        points = filtered_pts[['BPOGX', 'BPOGY']].values
    else:
        points = filtered_pts[['FPOGX', 'FPOGY', 'FPOGD']].values
    # print(points)
    # Scale points to the image dimensions
    points[:, 0] *= width
    points[:, 1] *= height
    # print(points)

    # Populate the heatmap with points using Gaussian distribution
    for point in points:
        x, y = math.floor(point[0]), math.floor(point[1])
        # print(x, y)
        if y == height:
            y -= 1
        if x == width:
            x -= 1
        if not use_fixation:
            heatmap[y, x] += 1
        else:
            heatmap[y, x] += point[2]
        # print(heatmap[y, x])

    # print(heatmap)

    # Apply Gaussian filter to create smooth heatmap
    heatmap = gaussian_filter(heatmap, sigma=sigma)

    heatmap_min = heatmap.min()
    heatmap_max = heatmap.max()
    heatmap_normalized = (heatmap - heatmap_min) / (heatmap_max - heatmap_min)

    # Make 0 values transparent in heatmap
    hot_cmap = plt.get_cmap('plasma')  # Get the original 'hot' colormap
    hot_colors = hot_cmap(np.arange(hot_cmap.N))  # Get the colormap colors
    hot_colors[:, -1] = np.linspace(0, 1, hot_cmap.N)  # Modify alpha values
    hot_cmap_with_alpha = LinearSegmentedColormap.from_list('hot_alpha', hot_colors)

    print(heatmap_normalized)
    # # Plot the heatmap
    # plt.imshow([[1, 0, 0,3, 0,5], [1, 0, 0,3, 0,5], [1, 0, 0,3, 0,5]], cmap='viridis', interpolation='none')
    # plt.imshow(heatmap_normalized, cmap='hot', interpolation='none')
    # plt.colorbar()
    # plt.title("Heatmap")
    # plt.show()

    # Step 1: Read the image
    background_image = plt.imread(background_image_path)

    # Step 2: Calculate aspect ratios
    heatmap_aspect_ratio = height / width
    image_aspect_ratio = background_image.shape[0] / background_image.shape[1]

    # Step 3: Calculate padding
    if heatmap_aspect_ratio != image_aspect_ratio:
        if heatmap_aspect_ratio > image_aspect_ratio:
            # The image is too wide, pad top and bottom
            pad_height = int(((background_image.shape[1] * heatmap_aspect_ratio) - background_image.shape[0]) / 2)
            padding = ((pad_height, pad_height), (0, 0), (0, 0))
        else:
            # The image is too tall, pad left and right
            pad_width = int(((background_image.shape[0] / heatmap_aspect_ratio) - background_image.shape[1]) / 2)
            padding = ((0, 0), (pad_width, pad_width), (0, 0))

        # Step 4: Apply padding
        background_image_padded = np.pad(background_image, padding, mode='constant', constant_values=255)
    else:
        background_image_padded = background_image

    # # Create a figure with the background image
    with plotting.paper_theme():
        plt.figure(figsize=figsize)
        plt.imshow(background_image_padded, extent=[0, width, height, 0])
        plt.imshow(heatmap_normalized, cmap=hot_cmap_with_alpha, alpha=1, extent=[0, width, height, 0])
        plt.colorbar(shrink=0.5, pad=0.01)
        plt.axis('off')
        plt.title(title, fontsize=10)

    plt.tight_layout()
    plt.savefig(figure_path, dpi=dpi)
    plt.close('all')

# generate_heatmap("./data/P23_S1_all_gaze.csv")
