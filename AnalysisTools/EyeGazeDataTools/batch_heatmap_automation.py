import os
import re
from heatmap import generate_heatmap

directory_path = "./data/"
figures_path = "./figures/"

pattern = r'(P\d{2}_S\d)\s?(#\s?)?.*?_all_gaze\.csv'
pattern_fixation = r'(P\d{2}_S\d)\s?(#\s?)?.*?_fixations\.csv'
# Get all file names in the directory
file_names = [f for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f))]
file_names_fixation = [f for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f))]

# Print all file names
for file_name in file_names:
    match = re.search(pattern, file_name)
    if match:
        # Extracting the desired part
        extracted_string = match.group(1).replace('_', ' ')
        print(f"Processing: {extracted_string}")
        print(f"File name: {file_name}")
        generate_heatmap(f"{directory_path}{file_name}", extracted_string,
                         f"{figures_path}{extracted_string.replace(' ', '_')}.png")

for file_name in file_names_fixation:
    match = re.search(pattern_fixation, file_name)
    if match:
        # Extracting the desired part
        extracted_string = match.group(1).replace('_', ' ')
        print(f"Processing: {extracted_string}")
        print(f"File name: {file_name}")
        generate_heatmap(f"{directory_path}{file_name}", extracted_string,
                         f"{figures_path}{extracted_string.replace(' ', '_')}_fixations.png", use_fixation=True)
