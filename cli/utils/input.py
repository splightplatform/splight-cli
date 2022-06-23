import click
from pydoc import locate

# def input_multiple(param: dict):
#     value = []
#     i = 0
#     _type = locate(param['type'])
#     click.secho(f"{param['name']} is multiple ({param['type']}). Enter empty to finish.", fg="blue")
#     while True:
#         val = click.prompt(f"{param['name']}[{i}]", type=str, default="", show_default=False)
#         if val == "":
#             break
#         value.append(_type(val))
#         i += 1
#     return value

def input_single(param: dict):
    default = 'None' if param['value'] is None and not param['required'] else param['value']
    name = f"{param['name']}{'*' if param['required'] else ''}"
    val = click.prompt(
        name,
        type=locate(param['type']),
        default=default,
        show_default=True
    )
    if val == 'None':
        val = None
    return val