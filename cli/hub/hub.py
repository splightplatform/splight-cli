import click
from ..cli import cli
from .utils import *
from ..context import pass_context, Context
from .component import Component


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
@click.argument("token", nargs=1, type=str)
@pass_context
def push_component(context: Context, type: str, path: str, token: str) -> None:
    """
    Push a component to the hub.\n
    Args:\n
        type: The type of the component.\n
        path: The path where the component is in local machine.\n
        token: Token given by Splight API.
    """
    try:
        component = Component(path)
        component.push(type, token)
        click.echo("Component pushed successfully")

    except Exception as e:
        click.echo(f"Error pushing component: {str(e)}")
        return


@cli.command()
@click.argument("type", nargs=1, type=str)
@click.argument("name", nargs=1, type=str)
@click.argument("version", nargs=1, type=str)
@click.argument("path", nargs=1, type=str)
@click.argument("token", nargs=1, type=str)
@pass_context
def pull_component(context: Context, type: str, name: str, version: str, path: str, token: str) -> None:
    """
    Pull a component from the hub.\n
    Args:\n
        type: The type of the component.\n
        name: The name of the component.\n
        version: The version of the component.\n
        path: The path where the component will be created.\n
        token: Token given by Splight API.
    """
    try:
        component = Component(path)
        component.pull(name, type, version, token)
        click.echo(f"Component {name}-{version} pulled successfully in {path}")

    except Exception as e:
        click.echo(f"Error pulling component of type {type}: {str(e)}")
        return


@cli.command()
@click.argument("type", nargs=1, type=str)
@click.argument("path", nargs=1, type=str)
@click.argument("instance_id", nargs=1, type=str)
@click.argument("run_spec", nargs=1, type=str)
@pass_context
def run_component(context: Context, type: str, path: str, instance_id: str, run_spec: str) -> None:
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
        component.run(type, instance_id, context.namespace, run_spec)
        click.echo(f"Component running successfully")

    except Exception as e:
        click.echo(f"Error running component: {str(e)}")
        return