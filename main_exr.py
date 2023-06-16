import os
import fileseq
import json
import subprocess
import re

oiiotool = "E://_GFX_library//OP3//exe//prod//vendor//bin//oiio//windows//oiiotool.exe"


def get_image_info(
    filepath,
):  # sourcery skip: use-getitem-for-re-match-groups, use-named-expression
    command = [
        oiiotool,
        "--info",
        "-v",
        filepath,
    ]
    process = subprocess.run(command, capture_output=True, text=True)
    output = process.stdout.split("\n")

    print(output)

    # Extract image size from oiio output
    size = "Unknown"
    resolution_pattern = re.compile(r"\b(\d+)\s*x\s*(\d+)\b")
    for line in output:
        match = re.search(resolution_pattern, line)
        if match:
            size = [int(match.group(1)), int(match.group(2))]
            break

    # Extract color space from oiio output, if present
    color_space = "Unknown"
    compression = "Unknown"
    for line in output:
        if "oiio:ColorSpace:" in line:
            color_space = line.split(":")[2].strip().replace('"', "")

        if "compression:" in line:
            compression = line.split(":")[1].strip().replace('"', "")

    # Check if image have alpha channel
    RGBA = "Unknown"
    for line in output:
        if "channel list:" in line:
            channels = line.split(":")[1].strip().replace('"', "")
            RGBA = "RGBA" if "A" in channels else "RGB"

    # Check pixel aspect ratio
    pixel_aspect_ratio = "Unknown"
    pixel_aspect_ratio_pattern = re.compile(r"PixelAspectRatio: (\d+(\.\d+)?)")
    for line in output:
        match = re.search(pixel_aspect_ratio_pattern, line)
        if match:
            pixel_aspect_ratio = float(match.group(1))

    # Check frame rate
    frame_rate = "Unknown"
    frame_rate_pattern_1 = re.compile(r"framesPerSecond:\s(\d+)/(\d+)\s\((\d+)\)")
    frame_rate_pattern_2 = re.compile(r"nuke/input/frame_rate:\s\"(\d+\.\d+)\"")

    for line in output:
        match1 = re.search(frame_rate_pattern_1, line)
        match2 = re.search(frame_rate_pattern_2, line)
        if match1:
            frame_rate = int(match1.group(3))
            break
        elif match2:
            frame_rate = float(match2.group(1))
            break

    return size, color_space, compression, RGBA, pixel_aspect_ratio, frame_rate


def create_jpg_proxy(filepath, output_filepath):
    command = [
        oiiotool,
        filepath,
        "-o",
        output_filepath,
    ]
    subprocess.run(command, capture_output=True, text=True)


def find_exr_sequences_in_directory(root):
    exr_sequences = []
    index = 0

    for dirpath, dirs, files in os.walk(root):
        fs = fileseq.findSequencesInList(files)

        for f in fs:
            if f.extension() == ".exr":
                sequence_name = f.basename()
                directory_path = dirpath
                index += 1

                # Find the heaviest frame in the sequence
                heaviest_frame_path = None
                heaviest_frame_size = 0

                for frame in f:
                    frame_path = os.path.join(dirpath, str(frame))
                    frame_size = os.path.getsize(frame_path)
                    if frame_size > heaviest_frame_size:
                        heaviest_frame_path = frame_path
                        heaviest_frame_size = frame_size

                # Create jpg proxy for the heaviest frame
                jpg_proxy_path = os.path.join(
                    directory_path, f"{sequence_name}_heaviest.jpg"
                )
                # create_jpg_proxy(heaviest_frame_path, jpg_proxy_path)

                (
                    image_size,
                    color_space,
                    compression,
                    RGBA,
                    pixel_aspect_ratio,
                    frame_rate,
                ) = get_image_info(heaviest_frame_path)

                exr_sequences.append(
                    {
                        "sequence_name": sequence_name,
                        "directory_path": os.path.abspath(directory_path),
                        "frame_range": [f.start(), f.end()],
                        "image_size": image_size,
                        "image_channels": RGBA,
                        "color_space": color_space,
                        "compression": compression,
                        "pixel_aspect_ratio": pixel_aspect_ratio,
                        "frame_rate": frame_rate,
                        "index": index,
                    }
                )

    return exr_sequences


root_path = "E:/Fidel/footage_classifier/footage_test"

try:
    sequences = find_exr_sequences_in_directory(root_path)
    print("Sequences found:", sequences)
except Exception as e:
    print("Error during sequence finding:", e)

try:
    # Save to a JSON file
    with open("sequences.json", "w") as f:
        json.dump(sequences, f, indent=4)
    print("JSON file written.")
except Exception as e:
    print("Error during JSON file writing:", e)
