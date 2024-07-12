import os
import re
import csv
from image_component_analysis import get_fixation_duration_per_image_component

directory_path = "./data/"
processed_data_path = "./data_processed/"

pattern = r'(P\d{2}_S\d)\s?(#\s?)?.*?_fixations\.csv'

# Get all file names in the directory
file_names = [f for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f))]

# Print all file names
for file_name in file_names:
    match = re.search(pattern, file_name)
    if match:
        # Extracting the desired part
        extracted_string = match.group(1).replace('_', ' ')
        print(f"Processing: {extracted_string}")
        print(f"File name: {file_name}")
        try:
            data = get_fixation_duration_per_image_component(f"{directory_path}{file_name}")
            save_file_name = f"{processed_data_path}{extracted_string.replace(' ', '_')}_image_component_analysis.csv"
            with open(save_file_name, mode='w', newline='') as file:
                keys = ""
                values = ""
                for key, item in data.items():
                    keys += key + ","
                    values += str(item) + ","
                file.writelines(keys[:-1] + "\n")
                file.writelines(values[:-1] + "\n")
        except KeyError:
            print(f"Error processing {file_name} with error {KeyError}, skipping file...")
