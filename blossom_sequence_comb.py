import json

sequence_dir = "./blossom-public/blossompy/src/sequences/woody/"

output_sequence_dir = "./blossom-public/blossompy/src/sequences/woody/cognitive/"


def combine_sequences(sequences: list, sequence_name=None):
    output_sequence = {
        "animation": "",
        "frame_list": []
    }
    last_sequence_duration = 0.0
    for seq in sequences:
        with open(sequence_dir + seq + "_sequence.json") as seq_file:
            sequence_data = json.load(seq_file)
            current_frame_list = sequence_data["frame_list"]
            for frame in current_frame_list:
                frame["millis"] += last_sequence_duration
            last_sequence_duration = current_frame_list[-1]["millis"]
            output_sequence["frame_list"].extend(current_frame_list)
            output_sequence["animation"] += sequence_data["animation"]
    if sequence_name is None:
        with open(output_sequence_dir + output_sequence["animation"] + "_sequence.json", "w") as outfile:
            json.dump(output_sequence, outfile, indent=2)
    else:
        with open(output_sequence_dir + sequence_name + "_sequence.json", "w") as outfile:
            output_sequence["animation"] = sequence_name
            json.dump(output_sequence, outfile, indent=2)


# combine_sequences(["yes", "no"], "yes_no")
