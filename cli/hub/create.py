import click
import os
from jinja2 import Template
from cli import cli
from .utils import *
from cli.context import pass_context, Context
from .settings import VALID_COMPONENTS

@cli.command()
@click.option('--component_type', type=click.Choice(VALID_COMPONENTS, case_sensitive=False), required=True)
@click.argument("component_name", nargs=1, type=str)
@click.argument("path", nargs=1, type=str)
@pass_context
def create_component(context: Context, component_type: str, component_name: str, path: str) -> None:
    """
    Create a component structure in path.\n
    Args:\n
        component_name: The name of the component.\n
        path: The path where the component will be created.
    """
    try:
        validate_component_name(component_name)
        validate_path_isdir(path)

        path = os.path.join(path, f"{component_name}")
        os.mkdir(path)

        component_files = ["__init__.py", f"{component_type}.py"]
        for file_name in component_files:
            template: Template = get_template(file_name)
            file = template.render(
                component_type=component_type,
                component_name=component_name
            )
            file_path = os.path.join(path, f"{file_name}")
            with open(file_path, "w+") as f:
                f.write(file)

        click.echo(f"Created component template in {path}")

    except Exception as e:
        click.echo(f"Error creating component of type {component_type}: {str(e)}")
        return