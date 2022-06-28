import click
import hashlib
import signal
import sys
import logging
from ..cli import component as cli_component
from ..utils import *
from ..auth import *
from ..context import Context, PrivacyPolicy
from ..settings import *
from .component import Component, ComponentAlreadyExistsException


def signal_handler(sig, frame):
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)


logger = logging.getLogger()
NO_IMPORT_PWD_HASH = "b9d7c258fce446158f0ad1779c4bdfb14e35b6e3f4768b4e3b59297a48804bb15ba7d04c131d01841c55722416428c094beb83037bac949fa207af5c91590dbf"


@cli_component.command()
@click.argument("type", nargs=1, type=str)
@click.argument("name", nargs=1, type=str)
@click.argument("version", nargs=1, type=str)
@needs_credentials
def create(context: Context, name: str, type: str, version: str) -> None:
    try:
        path = os.path.abspath(".")
        component = Component(path, context)
        component.create(name, type, version)
        click.secho(f"Component {name} created successfully in {path}", fg="green")

    except Exception as e:
        raise
        click.secho(f"Error creating component of type {type}: {str(e)}", fg="red")
        return


@cli_component.command()
@click.argument("type", nargs=1, type=str)
@click.argument("path", nargs=1, type=str)
@click.option("-f", "--force", is_flag=True, default=False, help="Force the component to be created even if it already exists.")
@click.option("-p", "--public", is_flag=True, default=False, help="Create a public component.")
@click.option("-ni", "--no-import", is_flag=True, default=False, help="Do not import component before pushing")
@needs_credentials
def push(context: Context, type: str, path: str, force: bool, public: bool, no_import: bool) -> None:
    try:
        if public:
            context.privacy_policy = PrivacyPolicy.PUBLIC
        if no_import:
            password = click.prompt(click.style("Enter password to push without checking component", fg="yellow"), hide_input=True, type=str)
            hash = hashlib.sha512(str(password).encode("utf-8")).hexdigest()
            if hash != NO_IMPORT_PWD_HASH:
                click.secho(f"Wrong password", fg="red")
                return
        component = Component(path, context)
        try:
            component.push(type, force, no_import)
            click.secho("Component pushed successfully to Splight Hub", fg="green")
        except ComponentAlreadyExistsException:
            value = click.prompt(click.style(f"This {type} already exists in Splight Hub (you can use -f to force pushing). Do you want to overwrite it? (y/n)", fg="yellow"), type=str)
            if value in ["y", "Y"]:
                component.push(type, force=True, no_import=no_import)
                click.secho("Component pushed successfully to Splight Hub", fg="green")
            else:
                click.secho("Component not pushed", fg="blue")

    except Exception as e:
        click.secho(f"Error pushing component: {str(e)}", fg="red")
        return


@cli_component.command()
@click.argument("type", nargs=1, type=str)
@click.argument("name", nargs=1, type=str)
@click.argument("version", nargs=1, type=str)
@needs_credentials
def pull(context: Context, type: str, name: str, version: str) -> None:
    try:
        path = os.path.abspath(".")
        component = Component(path, context)
        component.pull(name, type, version)
        click.secho(f"Component {name}-{version} pulled successfully in {path}", fg="green")

    except Exception as e:
        click.secho(f"Error pulling component of type {type}: {str(e)}", fg="red")
        return


@cli_component.command()
@click.argument("type", nargs=1, type=str)
@needs_credentials
def list(context: Context, type: str) -> None:
    try:
        logger.setLevel(logging.WARNING)
        handler = ComponentHandler(context)
        results = handler.list_components(type)
        Printer.print_dict(items=results, headers=['name', 'version'])
        return list

    except Exception as e:
        click.secho(f"Error listing component of type {type}: {str(e)}", fg="red")
        return


@cli_component.command()
@click.argument("type", nargs=1, type=str)
@click.argument("path", nargs=1, type=str)
@click.argument("run_spec", nargs=1, type=str)
@pass_context
def run(context: Context, type: str, path: str, run_spec: str) -> None:
    try:
        component = Component(path, context)
        click.secho(f"Running component...", fg="green")
        component.run(type, run_spec)

    except Exception as e:
        click.secho(f"Error running component: {str(e)}", fg="red")
        return


@cli_component.command()
@click.argument("type", nargs=1, type=str)
@click.argument("path", nargs=1, type=str)
@click.option('--namespace', '-n', help="Namespace of execution")
@click.option('--instance-id', '-i', help="ID of the running component.")
@click.option('--reset-input', '-r', is_flag=True, help="Set or Reset input parameters")
@pass_context
def test(context: Context, type: str, path: str, namespace: str = None, instance_id: str = None, reset_input: str = None) -> None:
    try:
        click.secho(f"Running component...", fg="green")
        component = Component(path, context)
        component.test(type, namespace, instance_id, reset_input)

    except Exception as e:
        logger.exception(e)
        click.secho(f"Error running component: {str(e)}", fg="red")
        return


@cli_component.command()
@click.argument("type", nargs=1, type=str)
@click.argument("path", nargs=1, type=str)
@pass_context
def install_requirements(context: Context, type: str, path: str) -> None:
    try:
        component = Component(path, context)
        click.secho(f"Installing component requirements...", fg="green")
        component.initialize()

    except Exception as e:
        click.secho(f"Error installing component requirements: {str(e)}", fg="red")
        return
