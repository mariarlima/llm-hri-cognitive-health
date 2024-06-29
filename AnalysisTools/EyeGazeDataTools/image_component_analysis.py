import json
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from scipy.ndimage import gaussian_filter
from utils import plotting
from utils import point_in_polygon


def load_annotation_file(file_path):
    with open(file_path, 'r') as f:
        shapes = json.load(f)
    print(f"Shapes Loaded:{json.dumps(shapes, indent=4)}")
    return shapes


def get_fixation_duration_per_image_component(data_path):
    analysis_result = {}
    cookie_image_path = "./images/The-Cookie-Theft-Picture-from-the-Boston-Diagnostic-Aphasia-Examination-For-the-PD-task.png"
    picnic_image_path = "./images/picnic.png"

    df = pd.read_csv(data_path)

    if df["MEDIA_NAME"][0] == "Cognitive Picture Description Task":
        background_image_path = cookie_image_path
    else:
        background_image_path = picnic_image_path
    # print(pandas_data.head())
    # Create a blank image with 16:9 aspect ratio
    filtered_pts = df[
        (df['FPOGX'] >= 0.0) & (df['FPOGX'] <= 1.0) & (df['FPOGY'] >= 0.0) & (df['FPOGY'] <= 1.0) & (df['FPOGV'] == 1)]

    points = filtered_pts[['FPOGX', 'FPOGY', 'FPOGD']].values

    annotation = load_annotation_file("./images/Cookie_theft_padded.annotation")

    for key in annotation.keys():
        analysis_result[key] = 0.0

    for point in points:
        x, y, duration = point[0], point[1], point[2]
        detect_shape = point_in_polygon.detect(x, y, annotation)
        if detect_shape is not None:
            analysis_result[detect_shape] += duration

    print(f"Analysis Result: {json.dumps(analysis_result, indent=4)}")
    return analysis_result

get_fixation_duration_per_image_component("./data/P21_S1_fixations.csv")
