import click
import os
import signal
import sys
import logging
import json
from cli.context import pass_context
from cli.cli import component as cli_component
from cli.utils import *
from cli.context import Context
from cli.constants import *
from cli.component.component import Component, ComponentAlreadyExistsException


def signal_handler(sig, frame):
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)


logger = logging.getLogger()


@cli_component.command()
@click.argument("name", nargs=1, type=str)
@click.argument("version", nargs=1, type=str)
@pass_context
def create(context: Context, name: str, version: str) -> None:
    try:
        component = Component(context)
        component.create(name, version)
        click.secho(f"Component {name} created successfully", fg="green")

    except Exception as e:
        click.secho(f"Error creating component: {str(e)}", fg="red")
        sys.exit(1)


@cli_component.command()
@click.argument("path", nargs=1, type=str)
@click.option("-f", "--force", is_flag=True, default=False, help="Force the component to be created even if it already exists.")
@pass_context
def push(context: Context, path: str, force: bool) -> None:
    try:
        component = Component(context)
        try:
            component.push(path, force)
            click.secho("Component pushed successfully to Splight Hub", fg="green")
        except ComponentAlreadyExistsException:
            value = click.prompt(click.style(f"This component already exists in Splight Hub (you can use -f to force pushing). Do you want to overwrite it? (y/n)", fg="yellow"), type=str)
            if value in ["y", "Y"]:
                component.push(path, force=True)
                click.secho("Component pushed successfully to Splight Hub", fg="green")
            else:
                click.secho("Component not pushed", fg="blue")

    except Exception as e:
        click.secho(f"Error pushing component: {str(e)}", fg="red")
        sys.exit(1)


@cli_component.command()
@click.argument("name", nargs=1, type=str)
@click.argument("version", nargs=1, type=str)
@pass_context
def pull(context: Context, name: str, version: str) -> None:
    try:
        path = os.path.abspath(".")
        component = Component(context)
        component.pull(name, version)
        click.secho(f"Component {name}-{version} pulled successfully in {path}", fg="green")

    except Exception as e:
        click.secho(f"Error pulling component: {str(e)}", fg="red")
        sys.exit(1)


@cli_component.command()
@click.argument("name", nargs=1, type=str)
@click.argument("version", nargs=1, type=str)
@pass_context
def delete(context: Context, name: str, version: str) -> None:
    try:
        response = click.prompt(click.style(f"Are you sure you want to delete {name}-{version}? This operation will delete the component from Splight Hub and it won't be recoverable. (y/n)", fg="yellow"), type=str, default="n", show_default=False)
        if response not in ["y", "Y"]:
            click.secho("Component not deleted", fg="blue")
            sys.exit(1)
        component = Component(context)
        component.delete(name, version)
        click.secho(f"Component {name}-{version} deleted successfully", fg="green")

    except Exception as e:
        logger.exception(e)
        click.secho(f"Error deleting component: {str(e)}", fg="red")
        sys.exit(1)


@cli_component.command()
@pass_context
def list(context: Context) -> None:
    try:
        results = Component(context).list()
        Printer.print_dict(items=results, headers=['name'])
        return list

    except Exception as e:
        click.secho(f"Error listing component: {str(e)}", fg="red")
        sys.exit(1)


@cli_component.command()
@click.argument("name", nargs=1, type=str)
@pass_context
def versions(context: Context, name: str) -> None:
    try:
        results = Component(context).versions(name)
        Printer.print_dict(items=results, headers=['name', 'version', 'verification', 'privacy_policy'])
        return list

    except Exception as e:
        click.secho(f"Error listing component: {str(e)}", fg="red")
        sys.exit(1)


@cli_component.command()
@click.argument("path", nargs=1, type=str)
@click.option('--input', '-i', help="Input values")
@pass_context
def run(context: Context, path: str, input: str = None) -> None:
    try:
        component = Component(context)
        click.secho("Running component...", fg="green")
        input = json.loads(input) if input else None
        component.run(path, input_parameters=input)
    except Exception as e:
        logger.exception(e)
        click.secho(f"Error running component: {str(e)}", fg="red")
        sys.exit(1)


@cli_component.command()
@click.argument("path", nargs=1, type=str)
@pass_context
def install_requirements(context: Context, path: str) -> None:
    try:
        component = Component(context)
        click.secho("Installing component requirements...", fg="green")
        component.install_requirements(path)
    except Exception as e:
        click.secho(f"Error installing component requirements: {str(e)}", fg="red")
        sys.exit(1)
