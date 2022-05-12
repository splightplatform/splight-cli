import click
from ..cli import cli
from .utils import *
from ..context import pass_context, Context
from .component import Component, SPEC_FILE, ComponentAlreadyExistsException
import traceback
import logging

logger = logging.getLogger()

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
        click.secho(f"Component {name} created successfully in {path}", fg="green")

    except Exception as e:
        click.secho(f"Error creating component of type {type}: {str(e)}", fg="red")
        return


@cli.command()
@click.argument("type", nargs=1, type=str)
@click.argument("path", nargs=1, type=str)
@click.option("-f", "--force", is_flag=True, default=False, help="Force the component to be created even if it already exists.")
@pass_context
def push(context: Context, type: str, path: str, force: bool) -> None:
    """
    Push a component to the hub.\n
    Args:\n
        type: The type of the component.\n
        path: The path where the component is in local machine.\n
    """

    try:
        component = Component(path)
        try:
            component.push(type, force)
            click.secho("Component pushed successfully to Splight Hub", fg="green")
        except ComponentAlreadyExistsException:
            value = click.prompt(click.style(f"This {type} already exists in Splight Hub (you can use -f to force pushing). Do you want to overwrite it? (y/n)", fg="yellow"), type=str)
            if value in ["y", "Y"]:
                component.push(type, force=True)
                click.secho("Component pushed successfully to Splight Hub", fg="green")
            else:
                click.secho("Component not pushed", fg="blue")

    except Exception as e:
        click.secho(f"Error pushing component: {str(e)}", fg="red")
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
        click.secho(f"Component {name}-{version} pulled successfully in {path}", fg="green")

    except Exception as e:
        click.secho(f"Error pulling component of type {type}: {str(e)}", fg="red")
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
        logger.setLevel(logging.WARNING)
        headers = {"Authorization": f"Token {SPLIGHT_HUB_TOKEN}"}
        list = []
        page = hub_api_get(f"{SPLIGHT_HUB_HOST}/{component_type}/", headers=headers)
        page = page.json()
        if page["results"]:
            list.extend(page["results"])
        while page["next"] is not None:
            page = hub_api_get(page["next"], headers=headers)
            page = page.json()
            if page["results"]:
                list.extend(page["results"])
        click.echo(json.dumps(list, indent=4))
        return list

    except Exception as e:
        click.secho(f"Error listing component of type {component_type}: {str(e)}", fg="red")
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
        click.secho(f"Running component...", fg="green")
        component.run(type, run_spec)

    except Exception as e:
        click.echo(traceback.format_exc())
        click.secho(f"Error running component: {str(e)}", fg="red")
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
        click.secho(f"Running component...", fg="green")
        component.test(type)

    except Exception as e:
        click.echo(traceback.format_exc())
        click.secho(f"Error running component: {str(e)}", fg="red")
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
        click.secho(f"Installing component requirements...", fg="green")
        component.initialize()

    except Exception as e:
        click.echo(traceback.format_exc())
        click.secho(f"Error installing component requirements: {str(e)}", fg="red")
        return