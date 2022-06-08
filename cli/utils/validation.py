import os

def validate_path_isdir(path: str) -> str:
    if not os.path.isdir(path):
        raise ValueError(f"Path provided: \"{path}\" is not a directory")
    return path