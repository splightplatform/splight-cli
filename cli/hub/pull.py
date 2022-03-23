import click
import requests
import zipfile
import os
from cli import cli, pass_context, Context
from .utils import *
from settings import API_URL
from .settings import VALID_COMPONENTS

@cli.command()
@click.option('--component_type', type=click.Choice(VALID_COMPONENTS, case_sensitive=False), required=True)
@click.argument("component_name", nargs=1, type=str)
@click.argument("version", nargs=1, type=str)
@click.argument("path", nargs=1, type=str)
@click.argument("token", nargs=1, type=str)
@pass_context
def pull_component(context: Context, component_type: str, component_name: str, version: str, path: str, token: str) -> None:
    """
    Pull a component from the hub.\n
    Args:\n
        component_name: The name of the component.\n
        version: The version of the component.\n
        path: The path where the component will be created.\n
        token: Token given by Splight API.
    """
    try:
        validate_path_isdir(path)
        headers = {
            'Authorization': token
        }
        data = {
            'component_type': component_type,
            'component_name': component_name,
            'version': version,
        }
        response = requests.post(f"{API_URL}/hub/pull/", data=data, headers=headers)

        if response.status_code != 200:
            if response.status_code == 404:
                raise Exception(f"Component not found")
            raise Exception(f"Failed to pull the component from splight hub")
            
        versioned_component_name = f"{component_name}-{version}"
        zip_filename = f"{versioned_component_name}.zip"
        try:
            with open(zip_filename, "wb") as f:
                f.write(response.content)

            component_path = os.path.join(path, versioned_component_name)
            with zipfile.ZipFile(zip_filename) as zip_ref:
                    os.mkdir(component_path)
                    zip_ref.extractall(component_path)
            click.echo(f"Component {component_name}-{version} pulled successfully in {path}")
        except:
            raise Exception(f"Failed to extract the component from splight hub to local machine. Make sure there's no directory called {versioned_component_name} in {path}")
        finally:
            os.remove(zip_filename)

    except Exception as e:
        click.echo(f"Error pulling component of type {component_type}: {str(e)}")
        return