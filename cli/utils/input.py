from functools import partial
from pydoc import locate
from typing import Dict, List, Type, Union

import click

Primitive = Union[int, str, float, bool]


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


def list_of(input_value: Union[List, str], param_type: Type = str) -> List:
    if isinstance(input_value, list):
        return input_value
    return [param_type(v.strip()) for v in input_value.split(",")]


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
    name = f"{'*' if required else ' '}{param_name} ({param_type})"
    param_type = locate(param["type"])
    if not param_type:
        param_type = str
    value_proc = None
    if param.get("multiple"):
        value_proc = partial(list_of, param_type=param_type)

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
