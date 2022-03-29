import os
import json

def get_json_from_file(file_path: str):
    if not os.path.isfile(file_path):
        raise Exception(f"String provided: \"{file_path}\" is not a file, please provide a filepath or use -fs flag")
    with open(file_path, 'r') as f:
        try:
            return json.load(f)
        except:
            raise Exception("File is not a valid JSON")