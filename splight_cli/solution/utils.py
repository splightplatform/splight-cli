import json
import re
import uuid
from collections import namedtuple
from pathlib import Path
from typing import Dict, Union

import typer
import yaml
from pydantic import BaseModel
from rich.console import Console
from rich.style import Style
from splight_lib.models import Asset, Component, File, RoutineObject

console = Console()

SplightTypes = Union[Asset, Component, RoutineObject, File]

MatchResult = namedtuple(
    "MatchResult", ["is_id", "type", "asset", "attribute"]
)


DEFAULT_STATE_PATH = "state.yml"
PRINT_STYLE = "bold black on white"
IMPORT_PREFIX = "imported_"


def to_dict(instance: SplightTypes) -> Dict:
    return json.loads(instance.model_dump_json())


def bprint(string: str):
    return console.print(string, style=Style(bold=True))


def bgprint(string: str):
    return console.print(string, style=Style(bold=True, color="green"))


def load_yaml(yaml_path: Path):
    with open(yaml_path, "r") as f:
        loaded_yaml = yaml.safe_load(f)
    return loaded_yaml


def save_yaml(yaml_path: Path, elem_to_save: Union[BaseModel, Dict]):
    bprint(f"Saving {yaml_path}...")
    dict_to_save = (
        elem_to_save
        if isinstance(elem_to_save, dict)
        else to_dict(elem_to_save)
    )
    with open(yaml_path, "w") as f:
        yaml.dump(dict_to_save, f, indent=2)


def is_valid_uuid(possible_uuid: str) -> bool:
    try:
        uuid.UUID(str(possible_uuid))
        return True
    except ValueError:
        return False


def get_ref_str(prefix: str, name: str) -> str:
    return f"{prefix}.{{{{{name}}}}}"


def confirm_or_yes(yes_to_all: bool, string: str) -> bool:
    return True if yes_to_all else typer.confirm(string)
