import json
import re
import uuid
from collections import namedtuple
from pathlib import Path
from typing import Dict, Union

import yaml
from pydantic import BaseModel
from rich.console import Console
from rich.style import Style
from splight_lib.models import Asset, Component, RoutineObject

from cli.solution.models import Solution

console = Console()

SplightTypes = Union[Asset, Component, RoutineObject]

MatchResult = namedtuple(
    "MatchResult", ["is_id", "type", "asset", "attribute"]
)


DEFAULT_STATE_PATH = "state.yml"
PRINT_STYLE = "bold black on white"


class MissingElement(Exception):
    ...


class ElemnentAlreadyDefined(Exception):
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


def save_yaml(yaml_path: Path, elem_to_save: Union[BaseModel, Dict]):
    bprint(f"Saving {yaml_path}...")
    dict_to_save = (
        elem_to_save
        if isinstance(elem_to_save, dict)
        else to_dict(elem_to_save)
    )
    with open(yaml_path, "w") as f:
        yaml.dump(dict_to_save, f, indent=2)


def check_files(plan: Solution, state: Solution):
    plan_assets = plan.assets
    state_assets = state.assets
    if len(plan_assets) != len(state_assets):
        raise ValueError(
            "The number of assets defined in the plan is different from the "
            "ones defined in the state file."
        )

    seen_state_assets = {a.name: 0 for a in state_assets}
    for asset in plan_assets:
        plan_asset_name = asset.name
        if plan_asset_name not in seen_state_assets.keys():
            raise MissingElement(
                f"Plan asset {plan_asset_name} was not found in the state "
                "assets."
            )
        seen_state_assets[plan_asset_name] += 1
        if seen_state_assets[plan_asset_name] > 1:
            raise ElemnentAlreadyDefined(
                f"The asset {plan_asset_name} is already defined. Asset names"
                " must be unique."
            )

    plan_components = plan.components
    state_components = state.components
    if len(plan_components) != len(state_components):
        raise ValueError(
            "The number of components defined in the plan is different from "
            "the ones defined in the state file."
        )

    seen_state_comps = {c.name: 0 for c in state_components}
    for comp in plan_components:
        plan_comp_name = comp.name
        if plan_comp_name not in seen_state_comps.keys():
            raise MissingElement(
                f"Plan component {plan_comp_name} was not found in the state "
                "components."
            )
        seen_state_comps[plan_comp_name] += 1
        if seen_state_comps[plan_comp_name] > 1:
            raise ElemnentAlreadyDefined(
                f"The component {plan_comp_name} is already defined. "
                "Component names must be unique."
            )


def is_valid_uuid(possible_uuid: str) -> bool:
    try:
        uuid.UUID(str(possible_uuid))
        return True
    except ValueError:
        return False


def parse_str_data_addr(data_addr_val: Dict[str, str]) -> MatchResult:
    """Parses a dictionary where the key 'asset' has a string of the form
    <local/engine>.{{<asset-name>}} and returns just the <asset-name>.

    Parameters
    ----------
    data_addr_val : Dict[str, str]
        Data address to process.

    Returns
    -------
    MatchResult
        Returns a named tuple with the asset, attribute, a type which can be
        either 'local' or 'engine' and a boolean which says if the asset and
        attribute names are ids or not.
    """
    asset = data_addr_val["asset"]
    attribute = data_addr_val["attribute"]
    if is_valid_uuid(asset) and is_valid_uuid(attribute):
        return MatchResult(
            is_id=True,
            type="engine",
            asset=asset,
            attribute=attribute,
        )
    local_or_engine, name_str = asset.split(".")
    regex = re.compile(r"{{(.*)}}")
    result = regex.search(name_str)
    return MatchResult(
        is_id=False,
        type=local_or_engine,
        asset=result.group(1),
        attribute=attribute,
    )
