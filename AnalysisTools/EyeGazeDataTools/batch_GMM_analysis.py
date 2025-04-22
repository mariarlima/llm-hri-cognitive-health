import os
import re
from GMM_analysis import get_eye_gaze_data, get_GMM_baseline, get_normalized_log_likelihood, get_Overall_Mask_GMM_baseline

directory_path = "./data/"
output_filepath = "./data_processed/Image_Components_GMM_results.csv"
output_filepath_overall_gmm = "./data_processed/Overall_GMM_results.csv"

verbose = False

pattern = r'(P\d{2}_S\d)\s?(#\s?)?.*?_all_gaze\.csv'
# Get all file names in the directory
file_names = [f for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f))]
baseline_cookie = get_GMM_baseline("Cognitive Picture Description Task", verbose=verbose)
overall_baseline_cookie = get_Overall_Mask_GMM_baseline("Cognitive Picture Description Task", verbose=verbose)
baseline_picnic = get_GMM_baseline("Picnic Task", verbose=verbose)
overall_baseline_picnic = get_Overall_Mask_GMM_baseline("Picnic Task", verbose=verbose)
print(baseline_cookie)
print(overall_baseline_cookie)
print(baseline_picnic)
print(overall_baseline_picnic)
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
            points[:, 0] *= 1920
            points[:, 1] *= 1080
            baseline_gmm = baseline_cookie if task == "Cognitive Picture Description Task" else baseline_picnic
            overall_baseline_gmm = overall_baseline_cookie if task == "Cognitive Picture Description Task" else overall_baseline_picnic
            score = get_normalized_log_likelihood(points, gmm=baseline_gmm, show_plot=False)
            score_overall_baseline = get_normalized_log_likelihood(points, gmm=overall_baseline_gmm, show_plot=False)
        except ValueError:
            score = float('nan')
            score_overall_baseline = float('nan')
        print(f"{extracted_string} GMM score: {score:.2f}")
        print(f"{extracted_string} Overall GMM score: {score_overall_baseline:.2f}")
        with open(output_filepath, "a") as f:
            f.write(f"{extracted_string},{score:.2f}\n")
        with open(output_filepath_overall_gmm, "a") as f_o:
            f_o.write(f"{extracted_string},{score_overall_baseline:.2f}\n")
