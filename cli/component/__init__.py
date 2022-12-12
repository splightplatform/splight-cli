import click
import os
import signal
import sys
import logging
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
NO_IMPORT_PWD_HASH = "b9d7c258fce446158f0ad1779c4bdfb14e35b6e3f4768b4e3b59297a48804bb15ba7d04c131d01841c55722416428c094beb83037bac949fa207af5c91590dbf"


@cli_component.command()
@click.argument("name", nargs=1, type=str)
@click.argument("version", nargs=1, type=str)
@pass_context
def create(context: Context, name: str, version: str) -> None:
    try:
        path = os.path.abspath(".")
        component = Component(path, context)
        component.create(name, version)
        click.secho(f"Component {name} created successfully in {path}", fg="green")

    except Exception as e:
        click.secho(f"Error creating component: {str(e)}", fg="red")
        sys.exit(1)


@cli_component.command()
@click.argument("path", nargs=1, type=str)
@click.option("-f", "--force", is_flag=True, default=False, help="Force the component to be created even if it already exists.")
@click.option("-p", "--public", is_flag=True, default=False, help="Create a public component.")
@pass_context
def push(context: Context, path: str, force: bool, public: bool = False) -> None:
    try:
        component = Component(path, context)
        try:
            component.push(force, public)
            click.secho("Component pushed successfully to Splight Hub", fg="green")
        except ComponentAlreadyExistsException:
            value = click.prompt(click.style(f"This component already exists in Splight Hub (you can use -f to force pushing). Do you want to overwrite it? (y/n)", fg="yellow"), type=str)
            if value in ["y", "Y"]:
                component.push(force=True, public=public)
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
        component = Component(path, context)
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
        path = os.path.abspath(".")
        component = Component(path, context)
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
        results = Component.list(context)
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
        results = Component.versions(context, name)
        Printer.print_dict(items=results, headers=['name', 'version', 'verification', 'privacy_policy'])
        return list

    except Exception as e:
        click.secho(f"Error listing component: {str(e)}", fg="red")
        sys.exit(1)


@cli_component.command()
@click.argument("path", nargs=1, type=str)
@click.option('--run-spec', '-rs', help="Run spec")
@pass_context
def run(context: Context, path: str, run_spec: str = None) -> None:
    try:
        component = Component(path, context)
        click.secho("Running component...", fg="green")
        component.run(run_spec)
    except Exception as e:
        click.secho(f"Error running component: {str(e)}", fg="red")
        sys.exit(1)


@cli_component.command()
@click.argument("path", nargs=1, type=str)
@pass_context
def install_requirements(context: Context, path: str) -> None:
    try:
        component = Component(path, context)
        click.secho("Installing component requirements...", fg="green")
        component.initialize()

    except Exception as e:
        click.secho(f"Error installing component requirements: {str(e)}", fg="red")
        sys.exit(1)
