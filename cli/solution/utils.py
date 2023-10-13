import json
from pathlib import Path
from typing import Any, Dict, Union

import yaml
from rich.console import Console
from rich.style import Style
from splight_lib.models import Asset, Component, RoutineObject

console = Console()

StrKeyDict = Dict[str, Any]
SplightTypes = Union[Asset, Component, RoutineObject]


class MissingElement(Exception):
    ...


def to_dict(instance):
    return json.loads(instance.json())


def bprint(string: str):
    return console.print(string, style=Style(bold=True))


def bgprint(string: str):
    return console.print(string, style=Style(bold=True, color="green"))


def load_yaml(yaml_path: Path):
    with open(yaml_path, "r") as f:
        loaded_yaml = yaml.safe_load(f)
    return loaded_yaml


def save_yaml(yaml_path: Path, yaml_dict: Dict):
    bprint(f"Saving {yaml_path}...")
    with open(yaml_path, "w") as f:
        yaml.dump(yaml_dict, f, indent=2)


def check_files(plan: Dict, state: Dict):
    plan_assets = plan["solution"]["assets"]
    state_assets = state["solution"]["assets"]
    if len(plan_assets) != len(state_assets):
        raise ValueError(
            "The number of assets defined in the plan is different from the "
            "ones defined in the state file."
        )

    state_asset_names = [a["name"] for a in state_assets]
    for asset in plan_assets:
        plan_asset_name = asset["name"]
        if plan_asset_name not in state_asset_names:
            raise MissingElement(
                f"Plan asset {plan_asset_name} was not found in the state "
                "assets."
            )

    plan_components = plan["solution"]["components"]
    state_components = state["solution"]["components"]
    if len(plan_components) != len(state_components):
        raise ValueError(
            "The number of components defined in the plan is different from "
            "the ones defined in the state file."
        )

    state_comp_names = [c["name"] for c in state_components]
    for comp in plan_components:
        plan_comp_name = comp["name"]
        if plan_comp_name not in state_comp_names:
            raise MissingElement(
                f"Plan component {plan_comp_name} was not found in the state "
                "components."
            )