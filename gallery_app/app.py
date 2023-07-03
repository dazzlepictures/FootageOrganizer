from flask import Flask, request
from flask_cors import CORS
import os
import subprocess

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes


@app.route("/")
def home():
    return "Home Page!"


@app.route("/openfolder")
def openfolder():
    file_to_open = request.args.get("path")  # Get the file from the query parameters
    file_to_open = os.path.realpath(file_to_open)
    # get format of the file
    file_extension = "." + file_to_open.split(".")[-1]
    print(file_extension)

    # Check the file extension and open with appropriate application
    if file_extension in [".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".exr"]:
        # If the file is an image, open with DJV
        subprocess.Popen([r"C:/Program Files/DJV2/bin/djv.exe", file_to_open])
    elif file_extension in [".mp4", ".avi", ".mov"]:
        # If the file is a video, open with VLC
        subprocess.Popen([r"C:/Program Files/VideoLAN/VLC/vlc.exe", file_to_open])
    else:
        return "File type not supported!"

    return "File opened!"


if __name__ == "__main__":
    app.run(debug=True)
