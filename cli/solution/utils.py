import json

import yaml
from rich.console import Console
from rich.style import Style

console = Console()


def bold_print(string):
    return console.print(string, style=Style(bold=True))


def load_yaml(yaml_path: str):
    with open(yaml_path, "r") as f:
        loaded_yaml = yaml.safe_load(f)
    return loaded_yaml


def load_json(json_path: str):
    with open(json_path, "r") as f:
        loaded_json = json.load(f)
    return loaded_json
