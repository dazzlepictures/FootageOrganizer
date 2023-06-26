import os
import fileseq
from media_info import (
    get_image_info,
    get_video_info,
    convert_frame_to_jpg,
    convert_frame_to_jpg_video,
)


def find_sequences_in_list(dirpath):
    sequences = []
    index = 0

    for root, dirs, files in os.walk(dirpath):
        fs = fileseq.findSequencesInList(files)

        for f in fs:
            # Get the extension of the file
            image_format = f.extension()

            first_frame_path = os.path.join(root, f[0])
            proxy_output_path = first_frame_path.replace(image_format, ".jpg")

            # replace \\ with / in the path
            proxy_output_path = proxy_output_path.replace("\\", "/")

            if (
                image_format in {".exr", ".jpg", ".png", ".bmp", ".tiff", ".jpeg"}
                and len(f) > 1
            ):
                sequence_name = f.basename().split(".")[0]
                directory_path = root
                convert_frame_to_jpg(first_frame_path, proxy_output_path)

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
                        "image_format": image_format,
                        "index": index,
                        "proxy_output_path": proxy_output_path,
                    }
                )

                index += 1

            elif image_format in {".mov", ".mp4", ".avi", ".mkv"}:
                print(f"frame start {f.start()}")
                sequence_name = f.basename().split(".")[0]
                directory_path = root
                convert_frame_to_jpg_video(
                    first_frame_path, proxy_output_path, f.start()
                )

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
                        "image_format": image_format,
                        "index": index,
                        "proxy_output_path": proxy_output_path,
                    }
                )

                index += 1

    return sequences
