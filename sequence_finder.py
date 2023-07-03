from file_operations import find_sequences_in_list
import json
import os

root_path = "E:/Fidel/footage_classifier/footage_test"

sequences = []
index = 0

try:
    index += 1
    sequences += find_sequences_in_list(root_path)
    print("Sequences found:")
except Exception as e:
    print("Error during sequence finding:", e)

try:
    # Save to a JSON file
    with open("./gallery_app/sequences.json", "w") as f:
        json.dump(sequences, f, indent=4)
    print("JSON file written.")
except Exception as e:
    print("Error during JSON file writing:", e)
