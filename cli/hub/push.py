import click
import os
import shutil
import requests
import sys
from cli import cli, pass_context, Context
from typing import Type
from .utils import *
from settings import API_URL
from .settings import VALID_COMPONENTS
import importlib

def import_component(component_name):
    try:
        return importlib.import_module(component_name)
    except Exception as e:
        raise Exception(f"Failed importing component {component_name} {str(e)}")

def validate_version(version):
    invalid_characters_version = ["/", "-"]
    if not isinstance(version, str):
        raise Exception(f"VERSION must be a string")
    if len(version) > 20:
        raise Exception(f"VERSION must be 20 characters maximum")
    if any(x in version for x in invalid_characters_version):
        raise Exception(f"VERSION cannot contain any of these: {invalid_characters_version}")


def validate_component(component):
    try:
        if not isinstance(component.COMPONENT_CLASS, Type):
            raise Exception(f"COMPONENT_CLASS is not a class")
        if component.COMPONENT_TYPE not in VALID_COMPONENTS:
            raise Exception(f"COMPONENT_TYPE is not a valid component type. Valid types are: {VALID_COMPONENTS}")
        validate_version(component.VERSION)


    except Exception as e:
        raise Exception(f"Failed to validate component: {str(e)}")

def get_component_zip(component_name, path):
        shutil.make_archive(component_name, 'zip', path)
        file = {}
        zip_file = f"{component_name}.zip"
        with open(zip_file, 'rb') as f:
            file['file'] = f.read()
        os.remove(zip_file)
        return file


@cli.command()
@click.option('--component_type', type=click.Choice(VALID_COMPONENTS, case_sensitive=False), required=True)
@click.option("-u/-c", "--update/--create", default=False)
@click.argument("path", nargs=1, type=str)
@click.argument("token", nargs=1, type=str)
@pass_context
def push_component(context: Context, component_type: str, update: bool, path: str, token: str) -> None:
    """
    Push a component to the hub.\n
    Args:\n
        path: The path where the component is in local machine.
        token: Token given by Splight API.
    """
    try:
        validate_path_isdir(path)
        component_directory_name = path.split(os.sep)[-1]

        sys.path.append(path)
        component = import_component(component_directory_name)
        validate_component(component)

        component_name = component.COMPONENT_CLASS.__name__
        component_version = component.VERSION

        file = get_component_zip(component_name, path)
        headers = {
            'Authorization': token
        }
        data = {
            'component_type': component_type,
            'component_name': component_name,
            'version': component_version
        }
        response = requests.post(f"{API_URL}/hub/push/", files=file, data=data, headers=headers)
        
        output_message = "Component pushed successfully"
        if response.status_code != 201:
            output_message = f"Error pushing component: {response.text}"

        click.echo(output_message)
        return

    except Exception as e:
        click.echo(f"Error pushing component: {str(e)}")
        return