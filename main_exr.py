import os
import fileseq
import json
import subprocess
import re

oiiotool = "E://_GFX_library//OP3//exe//prod//vendor//bin//oiio//windows//oiiotool.exe"

ffmpeg_path = "E:/_GFX_library/ffmpeg"
ffprobe_executable = "ffprobe.exe"  # Specify the executable file name


def get_video_info(filepath):
    command = [
        os.path.join(
            ffmpeg_path, ffprobe_executable
        ),  # Include the full path to ffprobe.exe
        "-v",
        "quiet",
        "-print_format",
        "json",
        "-show_streams",
        filepath,
    ]
    process = subprocess.run(command, capture_output=True, text=True)
    output = json.loads(process.stdout)

    # Get resolution
    width = output["streams"][0]["width"]
    height = output["streams"][0]["height"]
    size = [width, height]

    # Get color space
    color_space = output["streams"][0].get("color_space", "Unknown")

    # Get compression
    compression = output["streams"][0].get("codec_name", "Unknown")

    # Check if video has alpha channel
    RGBA = "RGBA" if "alpha" in output["streams"][0].get("pix_fmt", "") else "RGB"

    # Check pixel aspect ratio
    pixel_aspect_ratio = output["streams"][0].get("display_aspect_ratio", "Unknown")

    # Check frame rate
    frame_rate = output["streams"][0].get("r_frame_rate", "Unknown")
    if frame_rate != "Unknown":
        # Convert it to a number
        num, denom = map(int, frame_rate.split("/"))
        frame_rate = num / denom

    # Get number of frames
    nb_frames = output["streams"][0].get("nb_read_frames", "Unknown")

    print(output)

    return (
        size,
        color_space,
        compression,
        RGBA,
        pixel_aspect_ratio,
        frame_rate,
        nb_frames,
    )


def get_image_info(filepath):
    command = [
        oiiotool,
        "--info",
        "-v",
        filepath,
    ]
    process = subprocess.run(command, capture_output=True, text=True)
    output = process.stdout.split("\n")

    # Extract image size from oiio output
    size = "Unknown"
    resolution_pattern = re.compile(r"(\d+) x (\d+)")
    for line in output:
        match = re.search(resolution_pattern, line)
        if match:
            size = [int(match.group(1)), int(match.group(2))]
            break

    # Extract color space from oiio output, if present
    color_space = "Unknown"
    compression = "Unknown"
    for line in output:
        if "oiio:ColorSpace" in line:
            color_space = line.split(" ")[-1].strip().replace('"', "")

        if "compression:" in line:
            compression = line.split(" ")[-1].strip().replace('"', "")

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
    frame_rate_pattern_1 = re.compile(r"framesPerSecond: (\d+)/1 \((\d+)\)")
    frame_rate_pattern_2 = re.compile(r"nuke/input/frame_rate: \"(\d+\.\d+)\"")

    for line in output:
        match1 = re.search(frame_rate_pattern_1, line)
        match2 = re.search(frame_rate_pattern_2, line)
        if match1:
            frame_rate = int(match1.group(2))
            break
        elif match2:
            frame_rate = float(match2.group(1))
            break

    return size, color_space, compression, RGBA, pixel_aspect_ratio, frame_rate


def find_sequences_in_directory(root):
    sequences = []
    index = 0

    for dirpath, dirs, files in os.walk(root):
        fs = fileseq.findSequencesInList(files)

        for f in fs:
            # Get the extension of the file
            image_format = f.extension()

            if (
                image_format in {".exr", ".jpg", ".png", ".bmp", ".tiff", "jpeg"}
                and len(f) > 1
            ):
                sequence_name = f.basename().split(".")[0]
                directory_path = dirpath
                index += 1

                first_frame_path = os.path.join(dirpath, f[0])

                (
                    image_size,
                    color_space,
                    compression,
                    RGBA,
                    pixel_aspect_ratio,
                    frame_rate,
                ) = get_image_info(first_frame_path)

                sequences.append(
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
                        "image_format": image_format,  # add image format to the data
                        "index": index,
                    }
                )

            elif image_format in {".mov", ".mp4", ".avi", ".mkv"}:
                sequence_name = f.basename().split(".")[0]
                directory_path = dirpath
                index += 1

                (
                    image_size,
                    color_space,
                    compression,
                    RGBA,
                    pixel_aspect_ratio,
                    frame_rate,
                    nb_frames,
                ) = get_video_info(first_frame_path)

                sequences.append(
                    {
                        "sequence_name": sequence_name,
                        "directory_path": os.path.abspath(directory_path),
                        "frame_range": nb_frames,
                        "image_size": image_size,
                        "image_channels": RGBA,
                        "color_space": color_space,
                        "compression": compression,
                        "pixel_aspect_ratio": pixel_aspect_ratio,
                        "frame_rate": frame_rate,
                        "image_format": image_format,  # add image format to the data
                        "index": index,
                    }
                )

    return sequences


root_path = "E:/Fidel/footage_classifier/footage_test"
# root_path = "//truenas/storage01/_ELEMENTS"

try:
    sequences = find_sequences_in_directory(root_path)
    print("Sequences found:")
except Exception as e:
    print("Error during sequence finding:", e)

try:
    # Save to a JSON file
    with open("sequences.json", "w") as f:
        json.dump(sequences, f, indent=4)
    print("JSON file written.")
except Exception as e:
    print("Error during JSON file writing:", e)
