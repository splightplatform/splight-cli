import click
from ..cli import cli
from .utils import *
from ..context import pass_context, Context
from .component import Component, SPEC_FILE
from .storage import *
import traceback


@cli.command()
@click.argument("type", nargs=1, type=str)
@click.argument("name", nargs=1, type=str)
@click.argument("version", nargs=1, type=str)
@pass_context
def create(context: Context, name: str, type: str, version: str) -> None:
    """
    Create a component structure in path.\n
    Args:\n
        name: The name of the component.\n
        type: The type of the component.\n
        version: The version of the component.\n
        path: The path where the component will be created.
    """
    try:
        path = os.path.abspath(".")
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
def push(context: Context, type: str, path: str) -> None:
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
        raise
        click.echo(f"Error pushing component: {str(e)}")
        return


@cli.command()
@click.argument("type", nargs=1, type=str)
@click.argument("name", nargs=1, type=str)
@click.argument("version", nargs=1, type=str)
@pass_context
def pull(context: Context, type: str, name: str, version: str) -> None:
    """
    Pull a component from the hub.\n
    Args:\n
        type: The type of the component.\n
        name: The name of the component.\n
        version: The version of the component.\n
        path: The path where the component will be created.\n
    """
    try:
        path = os.path.abspath(".")
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
def list(context: Context, component_type: str) -> None:
    """
    List components of a given type.\n
    Args:\n
        component_type: The type of the component.\n
    """
    try:
        storage_client = S3HubClient()
        result = storage_client.list_components(component_type, SPEC_FILE)
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
def run(context: Context, type: str, path: str, run_spec: str) -> None:
    """
    Run a component from the hub.\n
    Args:\n
        type: The type of the component.\n
        path: The path where the component is in local machine.\n
        run_spec: The run spec of the component.
    """
    try:
        component = Component(path)
        click.echo(f"Running component...")
        component.run(type, run_spec)

    except Exception as e:
        click.echo(traceback.format_exc())
        click.echo(f"Error running component: {str(e)}")
        return

@cli.command()
@click.argument("type", nargs=1, type=str)
@click.argument("path", nargs=1, type=str)
@pass_context
def test(context: Context, type: str, path: str) -> None:
    """
    Run a component from the hub.\n
    Args:\n
        type: The type of the component.\n
        path: The path where the component is in local machine.\n
    """
    try:
        component = Component(path)
        click.echo(f"Running component...")
        component.test(type)

    except Exception as e:
        click.echo(traceback.format_exc())
        click.echo(f"Error running component: {str(e)}")
        return

@cli.command()
@click.argument("type", nargs=1, type=str)
@click.argument("path", nargs=1, type=str)
@pass_context
def install_requirements(context: Context, type: str, path: str) -> None:
    """
    Run a component from the hub.\n
    Args:\n
        type: The type of the component.\n
        path: The path where the component is in local machine.\n
    """
    try:
        component = Component(path)
        click.echo(f"Installing component requirements...")
        component.initialize(type)

    except Exception as e:
        click.echo(traceback.format_exc())
        click.echo(f"Error running component: {str(e)}")
        return