import click
from pydoc import locate

def input_single(param: dict):
    default = 'None' if param['value'] is None and not param['required'] else param['value']
    name = f"{param['name']}{'*' if param['required'] else ''}"
    val = click.prompt(
        name,
        type=locate(param['type']),
        default=default,
        show_default=True
    )
    if isinstance(val, str):
        val = val.strip(" ")
    if val == 'None':
        val = None
    return val