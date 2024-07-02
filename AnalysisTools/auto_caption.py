import torch
import whisper
import datetime
import argparse
import json
import os


def transcribe_and_return_raw_data(model, audio_file):
    return model.transcribe(audio_file, word_timestamps=True)


def format_timestamp(seconds):
    # Convert the seconds to hours, minutes, and seconds
    td = datetime.timedelta(seconds=seconds)
    time_str = str(td)

    # Split into main time and microseconds part
    if '.' in time_str:
        main_time, microseconds = time_str.split('.')
        milliseconds = microseconds[:3]
    else:
        main_time = time_str
        milliseconds = "000"

    return f"{main_time},{milliseconds}"


# def format_timestamp(seconds):
#     return str(datetime.timedelta(seconds=seconds)).replace(".", ",")


def transcribe_and_generate_srt(model, audio_file):
    result = model.transcribe(audio_file)

    segments = result["segments"]

    srt = []
    for i, segment in enumerate(segments):
        start = format_timestamp(segment["start"])
        end = format_timestamp(segment["end"])
        text = segment["text"]

        srt.append(f"{i + 1}\n{start} --> {end}\n{text}\n")

    srt_content = "\n".join(srt)
    return srt_content


def transcribe_and_generate_srt_and_text(model, audio_file):
    result = model.transcribe(audio_file)

    segments = result["segments"]

    plain_text = []
    srt = []
    for i, segment in enumerate(segments):
        text = segment["text"]

        start = format_timestamp(segment["start"])
        end = format_timestamp(segment["end"])

        srt.append(f"{i + 1}\n{start} --> {end}\n{text}\n")
        plain_text.append(f"{text}")

    plain_text_content = "\n".join(plain_text)
    srt_content = "\n".join(srt)
    return plain_text_content, srt_content


# whisper_model_id = "base.en"
# audio_file = "../Experiments.mp3"

# Create the parser
parser = argparse.ArgumentParser(description="Auto Captioning Tool CLI")

# Add the arguments
parser.add_argument('-f', '--file', type=str, required=True, help="Input file to transcribe.")
# parser.add_argument('-o', '--output', type=str, required=True, help="The output file")
parser.add_argument('-m', '--model', type=str, required=False, help="Whisper model ID", default="base.en")
parser.add_argument('-r', '--raw', type=bool, required=False, help="Output raw value.", default=False)

# Parse the arguments
args = parser.parse_args()

dir_name = os.path.dirname(args.file)
base_name = os.path.basename(args.file)

# Split the base name into the name and extension
name, _ = os.path.splitext(base_name)

# Construct the output file name
ext = "srt"
if args.raw:
    ext = "json"
output_file = os.path.join(dir_name, f"{name}.{ext}")

if torch.cuda.is_available():
    device = torch.device("cuda")
else:
    device = "cpu"
whisper_model = whisper.load_model(args.model).to(device)

if args.raw:
    raw_data = transcribe_and_return_raw_data(whisper_model, args.file)

    with open(output_file, "w") as f:
        json.dump(raw_data, f, indent=4)

    print(f"Raw data file generated: {output_file}")
else:
    srt_content = transcribe_and_generate_srt(whisper_model, args.file)

    with open(output_file, "w") as f:
        f.write(srt_content)

    print(f"SRT file generated: {output_file}")
