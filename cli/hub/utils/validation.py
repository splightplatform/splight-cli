import os
from ..settings import VALID_COMPONENTS


def validate_component_name(component_name: str) -> None:
    if not component_name[0].isupper():
        raise ValueError(f"Component class name: {component_name} first letter must be capitalized")


def validate_path_isdir(path: str) -> None:
    if not os.path.isdir(path):
        raise ValueError(f"Path provided: \"{path}\" is not a directory")


def validate_version(version):
    invalid_characters_version = ["/", "-"]
    if not isinstance(version, str):
        raise Exception(f"VERSION must be a string")
    if len(version) > 20:
        raise Exception(f"VERSION must be 20 characters maximum")
    if any(x in version for x in invalid_characters_version):
        raise Exception(f"VERSION cannot contain any of these characters: {invalid_characters_version}")