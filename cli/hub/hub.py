import click
import requests
from ..cli import cli
from .utils import *
from ..context import pass_context, Context
from .component import Component
from .settings import API_URL
from splight_models import StorageFile
from splight_lib.storage import StorageClient
import traceback


@cli.command()
@click.argument("type", nargs=1, type=str)
@click.argument("name", nargs=1, type=str)
@click.argument("version", nargs=1, type=str)
@click.argument("path", nargs=1, type=str)
@pass_context
def create_component(context: Context, name: str, type: str, version: str, path: str) -> None:
    """
    Create a component structure in path.\n
    Args:\n
        name: The name of the component.\n
        type: The type of the component.\n
        version: The version of the component.\n
        path: The path where the component will be created.
    """
    try:
        component = Component(path)
        component.create(name, type, version)
        click.echo(f"Component {name} created successfully in {path}")

    except Exception as e:
        click.echo(f"Error creating component of type {type}: {str(e)}")
        return


@cli.command()
@click.argument("type", nargs=1, type=str)
@click.argument("path", nargs=1, type=str)
@pass_context
def push_component(context: Context, type: str, path: str) -> None:
    """
    Push a component to the hub.\n
    Args:\n
        type: The type of the component.\n
        path: The path where the component is in local machine.\n
        token: Token given by Splight API.
    """

    try:
        component = Component(path)
        component.push(type)
        click.echo("Component pushed successfully")

    except Exception as e:
        click.echo(f"Error pushing component: {str(e)}")
        return


@cli.command()
@click.argument("type", nargs=1, type=str)
@click.argument("name", nargs=1, type=str)
@click.argument("version", nargs=1, type=str)
@click.argument("path", nargs=1, type=str)
@pass_context
def pull_component(context: Context, type: str, name: str, version: str, path: str) -> None:
    """
    Pull a component from the hub.\n
    Args:\n
        type: The type of the component.\n
        name: The name of the component.\n
        version: The version of the component.\n
        path: The path where the component will be created.\n
    """
    try:
        component = Component(path)
        component.pull(name, type, version)
        click.echo(f"Component {name}-{version} pulled successfully in {path}")

    except Exception as e:
        click.echo(f"Error pulling component of type {type}: {str(e)}")
        return


@cli.command()
@click.argument("component_type", nargs=1, type=str)
#@click.argument("token", nargs=1, type=str)
@pass_context
def list_component(context: Context, component_type: str) -> None:
    """
    List components of a given type.\n
    Args:\n
        component_type: The type of the component.\n
    """
    try:
        hub_directory = f"{Component.SPLIGHT_HUB_PUBLIC_DIRECTORY}/{component_type}"
        storage_client = StorageClient(hub_directory)
        queryset = storage_client.get(StorageFile)
        result = []
        components = set()
        for storage_file in queryset:
            component_versioned_name = storage_file.dir.id.split('/')[0]
            if component_versioned_name not in components:
                if storage_file.file == Component.SPEC_FILE:
                    storage_client.download(StorageFile, storage_file, "/tmp/spec.json")
                    spec_file = open("/tmp/spec.json", "r")
                    result.append(json.load(spec_file))
                    components.add(component_versioned_name)

        click.echo(json.dumps(result, indent=4))
        return result

    except Exception as e:
        click.echo(f"Error pulling component of type {component_type}: {str(e)}")
        return


@cli.command()
@click.argument("type", nargs=1, type=str)
@click.argument("path", nargs=1, type=str)
@click.argument("run_spec", nargs=1, type=str)
@pass_context
def run_component(context: Context, type: str, path: str, run_spec: str) -> None:
    """
    Run a component from the hub.\n
    Args:\n
        type: The type of the component.\n
        path: The path where the component is in local machine.\n
        instance_id: The instance id of the component.\n
        run_spec: The run spec of the component.
    """
    try:
        component = Component(path)
        click.echo(f"Running component...")
        component.run(type, context.namespace, run_spec)
        click.echo(f"Component runned successfully")

    except Exception as e:
        click.echo(traceback.format_exc())
        click.echo(f"Error running component: {str(e)}")
        return