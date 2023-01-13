import os
import yaml


def get_yaml_from_file(file_path: str):
    if not os.path.isfile(file_path):
        raise Exception(f"String provided: \"{file_path}\" is not a file, please provide a filepath or use -fs flag")
    with open(file_path, 'r') as f:
        try:
            data = yaml.load(f, Loader=yaml.FullLoader)
            return data if data is not None else {}
        except yaml.YAMLError as e:
            raise Exception("File is not a valid YAML") from e


def save_yaml_to_file(payload: str, file_path: str):
    with open(file_path, 'w+') as f:
        yaml.Dumper.ignore_aliases = lambda *args : True  # TOO RISKY to add refs on repetitions
        yaml.dump(payload, f)
