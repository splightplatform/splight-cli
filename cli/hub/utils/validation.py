import os
from ..settings import VALID_COMPONENTS


def validate_component_name(component_name: str) -> None:
    if not component_name[0].isupper():
        raise ValueError(f"Component class name: {component_name} first letter must be capitalized")


def validate_path_isdir(path: str) -> None:
    if not os.path.isdir(path):
        raise ValueError(f"Path provided: \"{path}\" is not a directory")