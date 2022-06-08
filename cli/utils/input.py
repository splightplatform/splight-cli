import click
from pydoc import locate

def input_multiple(param: dict):
    value = []
    i = 0
    _type = locate(param['type'])
    click.secho(f"{param['name']} is multiple ({param['type']}). Enter empty to finish.", fg="blue")
    while True:
        val = click.prompt(f"{param['name']}[{i}]", type=str, default="", show_default=False)
        if val == "":
            break
        value.append(_type(val))
        i += 1
    return value

def input_single(param: dict):
    val = click.prompt(f"{param['name']}", type=locate(param['type']), default="", show_default=False)
    return val