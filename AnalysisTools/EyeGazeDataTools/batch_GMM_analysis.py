import os
import re
from GMM_analysis import get_eye_gaze_data, get_GMM_baseline, get_normalized_log_likelihood

directory_path = "./data/"
output_filepath = "./data_processed/GMM_results.csv"

pattern = r'(P\d{2}_S\d)\s?(#\s?)?.*?_all_gaze\.csv'
# Get all file names in the directory
file_names = [f for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f))]
baseline_cookie = get_GMM_baseline("Cognitive Picture Description Task", verbose=False)
baseline_picnic = get_GMM_baseline("Picnic Task", verbose=False)
# Print all file names
for file_name in file_names:
    match = re.search(pattern, file_name)
    if match:
        # Extracting the desired part
        extracted_string = match.group(1).replace('_', ' ')
        print(f"Processing: {extracted_string}")
        # print(f"File name: {file_name}")
        try:
            points, task = get_eye_gaze_data(f"{directory_path}{file_name}")
            baseline_gmm = baseline_cookie if task == "Cognitive Picture Description Task" else baseline_picnic
            score = get_normalized_log_likelihood(points, gmm=baseline_gmm, show_plot=False)
        except ValueError:
            score = float('nan')
        print(f"{extracted_string} GMM score: {score:.2f}")
        with open(output_filepath, "a") as f:
            f.write(f"{extracted_string},{score:.2f}\n")
