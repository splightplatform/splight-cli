from ast import literal_eval
from functools import partial
from pydoc import locate
from typing import Dict, List, Type, Union

import click

Primitive = Union[int, str, float, bool]


def prompt_data_address_value():
    while True:
        asset_id = click.prompt(
            text="Asset ID",
            type=str,
            default=None,
        )
        if asset_id:
            break
        else:
            click.echo("Asset ID cannot be empty. Please try again.")

    while True:
        attribute_id = click.prompt(
            text="Attribute ID",
            type=str,
            default=None,
        )
        if attribute_id:
            break
        else:
            click.echo("Attribute ID cannot be empty. Please try again.")

    return {"asset": asset_id, "attribute": attribute_id}


def prompt_param(param: Dict[str, Primitive], prefix: str = "") -> Primitive:
    """Prompt the user for a single parameter

    Parameters
    ----------
    param: Dict
        The parameter to prompt
    prefix: str
        Prefix for the parameter name

    Returns
    -------
    Primitive
    """
    param_name = param["name"]
    new_value = input_single(
        {
            "name": f"{prefix} {param_name}",
            "type": param["type"],
            "required": param.get("required", True),
            "multiple": param.get("multiple", False),
            "value": param.get("value"),
        }
    )
    return new_value


def list_of(input_value: str, param_type: Type = str) -> List:
    try:
        values = literal_eval(input_value)
    except:
        return None

    if not isinstance(values, List):
        return None
    if not all([isinstance(elem, param_type) for elem in values]):
        return None

    return values


def input_single(param: Dict[str, Primitive]) -> Primitive:
    """Prompt user for input for a single parameter

    Parameters
    ----------
    param : Dict[str, Primitive]

    Returns
    -------
    Primitive the value given by the user
    """
    default = (
        "None"
        if param.get("value") is None and not param["required"]
        else param["value"]
    )
    required = param.get("required", False)
    param_name = param.get("name", "")
    param_type = param.get("type")
    multiple = param.get("multiple")
    name = f"{'*' if required else ' '}{param_name} {f'List[{param_type}]' if multiple else f'({param_type})'}"
    param_type = locate(param["type"])
    if not param_type:
        param_type = str
    value_proc = None
    if multiple:
        value_proc = partial(list_of, param_type=param_type)

    val = None
    while not val:
        val = click.prompt(
            text=name,
            type=param_type,
            default=default,
            value_proc=value_proc,
        )

    if isinstance(val, str):
        val = val.strip(" ")
        if not val:
            val = None
    if val == "None":
        val = None
    return val
