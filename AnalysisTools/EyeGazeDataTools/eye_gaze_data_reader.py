import pandas as pd


def get_eye_gaze_data(file_path, is_fixation=False):
    df = pd.read_csv(file_path)
    if not is_fixation:
        filtered_pts = df[
            (df['BPOGX'] >= 0.0) & (df['BPOGX'] <= 1.0) & (df['BPOGY'] >= 0.0) & (df['BPOGY'] <= 1.0) & (
                    df['BPOGV'] == 1)]
    else:
        filtered_pts = df[
            (df['FPOGX'] >= 0.0) & (df['FPOGX'] <= 1.0) & (df['FPOGY'] >= 0.0) & (df['FPOGY'] <= 1.0) & (
                    df['FPOGV'] == 1) & (df['FPOGD'] > 0.2)]
    if not is_fixation:
        points = filtered_pts[['BPOGX', 'BPOGY']].values
    else:
        points = filtered_pts[['FPOGX', 'FPOGY', 'FPOGD']].values
    return points

# print(get_eye_gaze_data("data/P23_S1_all_gaze.csv"))
