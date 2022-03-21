import click
import os
import shutil
import requests
from cli import cli, pass_context, Context
from .utils import *
from settings import API_URL

@cli.command()
@click.option('--component_type', type=click.Choice(VALID_COMPONENTS, case_sensitive=False), required=True)
@click.argument("component_name", nargs=1, type=str)
@click.argument("path", nargs=1, type=str)
@pass_context
def push_component(context: Context, component_type: str, component_name: str, path: str) -> None:
    """
    Push a component to the hub.\n
    Args:\n
        component_name: The name of the component.\n
        path: The path where the component is in local machine.
    """
    try:
        validate_component_name(component_name)
        validate_path_isdir(path)

        shutil.make_archive(component_name, 'zip', component_name)
        files = {}
        zip_file = f"{component_name}.zip"
        
        with open(zip_file, 'rb') as f:
            files['file'] = f.read()

        headers = {'Authorization': 'Splight backdoor'}
        data = {
            'component_type': component_type,
            'component_name': component_name
        }
        response = requests.post(f"{API_URL}/hub/push/", files=files, data=data, headers=headers)
        os.remove(zip_file)

        if response.status_code != 201:
            click.echo(f"Error pushing component: {response.text}")
            return
    except Exception as e:
        click.echo(f"Error pushing component: {str(e)}")
        return