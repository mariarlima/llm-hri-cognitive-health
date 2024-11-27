import torch
import whisper
import datetime
import argparse
import os


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
