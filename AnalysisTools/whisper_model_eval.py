import argparse
import os
import glob
import difflib
import whisper
import torch
import gc

from auto_caption_lib import transcribe_and_generate_srt_and_text


def get_video_files(directory):
    video_files = []
    for video_format in ('*.mp4', '*.flv', '*.avi', '*.mov', '*.wmv'):  # add or remove video formats as needed
        video_files.extend(glob.glob(os.path.join(directory, video_format)))
    return video_files


def string_similarity(str1, str2):
    sequence_matcher = difflib.SequenceMatcher(None, str1, str2)
    return sequence_matcher.ratio()


def transcribe_and_save_results(whisper_model_id, whisper_model, video_filename, directory, filename):
    print(f"Transcribing {video_filename} using {whisper_model_id}...")
    plain_text_content, srt_content = transcribe_and_generate_srt_and_text(whisper_model, video_filename)
    current_results[whisper_model_id] = plain_text_content

    output_plain_text_file = os.path.join(directory, f"{filename}_{whisper_model_id.replace('.', '_')}_plain_text.txt")
    output_srt_file = os.path.join(directory, f"{filename}_{whisper_model_id.replace('.', '_')}.srt")
    with open(output_plain_text_file, "w") as f:
        f.write(plain_text_content)
    with open(output_srt_file, "w") as f:
        f.write(srt_content)
    return plain_text_content, srt_content


whisper_model_ids = ["tiny.en", "base.en", "small.en"]

# Create the parser
parser = argparse.ArgumentParser(description="Auto Whisper Model Evaluation Tool CLI")

# Add the arguments
parser.add_argument('-f', '--file', type=str, required=True, help="Directory contains video files.")

parser.add_argument('-r', '--reload', type=bool, required=False, help="Unload and reload base model to save VRAM.",
                    default=False)
# Parse the arguments
args = parser.parse_args()

dir_name = os.path.dirname(args.file)
# base_name = os.path.basename(args.file)

for video_file in get_video_files(args.file):
    print(f"Evaluating {video_file}...")
    base_name = os.path.basename(video_file)
    name, _ = os.path.splitext(base_name)
    current_results = {}

    if torch.cuda.is_available():
        device = torch.device("cuda")
    else:
        device = "cpu"
    baseline_model = whisper.load_model(whisper_model_ids[-1]).to(device)
    baseline_result, _ = transcribe_and_save_results(whisper_model_ids[-1], baseline_model, video_file, dir_name, name)
    current_results[whisper_model_ids[-1]] = baseline_result

    if args.reload:
        del baseline_model
        gc.collect()

    whisper_models = {}
    for model_id in whisper_model_ids[:-1]:
        whisper_models[model_id] = whisper.load_model(model_id).to(device)

    for model_id in whisper_model_ids[:-1]:
        baseline_result, _ = transcribe_and_save_results(model_id, whisper_models[model_id], video_file, dir_name, name)
        current_results[model_id] = baseline_result

    eval_summary_content = f"Evaluation result for {video_file}:\n"
    for model_id in whisper_model_ids:
        similarity = string_similarity(current_results[whisper_model_ids[-1]], current_results[model_id])
        print(f"Similarity between {whisper_model_ids[-1]} and {model_id}: {similarity:.2f}")
        eval_summary_content.join(f"{model_id}: {similarity:.2f}\n")

    output_eval_summary = os.path.join(dir_name, f"{name}_eval_summary.txt")
    with open(output_eval_summary, "w") as f:
        f.write(eval_summary_content)
