#!/bin/bash                                                                     

video_ext=("mp4" "mov")

for ext in "${video_ext[@]}"; do
    for file in *."$ext"; do
        if [[ -f "$file" ]]; then
            echo "Processing $file"
            python ~/Feiyang/whisper-diarization/diarize.py -a "$file" --whisper-model large
        fi
    done
done

