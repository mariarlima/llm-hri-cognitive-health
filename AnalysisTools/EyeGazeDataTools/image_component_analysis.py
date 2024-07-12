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
    # print(f"Shapes Loaded:{json.dumps(shapes, indent=4)}")
    return shapes


def get_fixation_duration_per_image_component(data_path):
    analysis_result = {}
    cookie_image_path = "./images/The-Cookie-Theft-Picture-from-the-Boston-Diagnostic-Aphasia-Examination-For-the-PD-task.png"
    picnic_image_path = "./images/picnic.png"

    df = pd.read_csv(data_path)

    if df["MEDIA_NAME"][0] == "Cognitive Picture Description Task":
        background_image_path = cookie_image_path
        annotation = load_annotation_file("./images/Cookie_theft_padded.annotation")
    else:
        background_image_path = picnic_image_path
        annotation = load_annotation_file("./images/Picnic_padded.annotation")
    # print(pandas_data.head())
    # Create a blank image with 16:9 aspect ratio
    filtered_pts = df[
        (df['FPOGX'] >= 0.0) & (df['FPOGX'] <= 1.0) & (df['FPOGY'] >= 0.0) & (df['FPOGY'] <= 1.0) & (df['FPOGV'] == 1)]

    points = filtered_pts[['FPOGX', 'FPOGY', 'FPOGD']].values

    for key in annotation.keys():
        analysis_result[key] = 0.0

    surroundings = 0.0
    image_component_duration = 0.0

    for point in points:
        x, y, duration = point[0], point[1], point[2]
        detect_shapes = point_in_polygon.detect(x, y, annotation)
        if detect_shapes is not None:
            for shape_key in detect_shapes:
                analysis_result[shape_key] += duration
            image_component_duration += duration
        else:
            surroundings += duration

    # print(f"Analysis Result: {json.dumps(analysis_result, indent=4)}")
    # print(f"Surroundings: {surroundings}")
    # print(f"Image Components: {image_component_duration}")
    final_result = {}
    for key in analysis_result.keys():
        final_result[key] = analysis_result[key]
    final_result["Surroundings"] = surroundings
    final_result["Image Components"] = image_component_duration
    total_duration = surroundings + image_component_duration
    for key in final_result.keys():
        final_result[key] = round(final_result[key] / total_duration, 2)

    # print(f"Final Result: {json.dumps(final_result, indent=4)}")
    return analysis_result

# get_fixation_duration_per_image_component("./data/P21_S1_fixations.csv")
