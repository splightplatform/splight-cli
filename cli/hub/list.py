import click
import requests
import json
from cli import cli, pass_context, Context
from .utils import *
from settings import API_URL

@cli.command()
@click.argument("component_type", nargs=1, type=str)
@click.argument("token", nargs=1, type=str)
@pass_context
def list_component(context: Context, component_type: str, token: str) -> None:
    """
    List components of a given type.\n
    Args:\n
        token: Token given by Splight API.
    """
    try:
        headers = {
            'Authorization': token
        }
        response = requests.get(f"{API_URL}/hub/list/?component_type={component_type}", headers=headers)
        click.echo(json.dumps(response.json(), sort_keys=True, indent=4))
    except Exception as e:
        click.echo(f"Error pulling component of type {component_type}: {str(e)}")
        return