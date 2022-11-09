from functools import partial
from pydoc import locate
from typing import List, Type, Union

import click


def list_of(input_value: Union[List, str], param_type: Type = str):
    if isinstance(input_value, list):
        return input_value
    return [param_type(v.strip()) for v in input_value.split(",")]


def input_single(param: dict):
    default = (
        "None"
        if param.get("value") is None and not param["required"]
        else param["value"]
    )
    name = (
        f"{'*' if param['required'] else ''}{param['name']}: {param['type']}"
    )
    param_type = locate(param["type"])
    if not param_type:
        param_type = str
    value_proc = None
    if param.get("multiple"):
        value_proc = partial(list_of, param_type=param_type)

    val = click.prompt(
        name,
        type=param_type,
        default=default,
        show_default=True,
        value_proc=value_proc,
    )
    if isinstance(val, str):
        val = val.strip(" ")
    if val == "None":
        val = None
    return val
