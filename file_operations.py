import os
import fileseq
from media_info import get_image_info, get_video_info


def find_sequences_in_list(files, dirpath):
    sequences = []
    index = 0

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
