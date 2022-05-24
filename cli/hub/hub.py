import click
from functools import update_wrapper
import hashlib
import signal
import sys
import traceback
import logging
from ..cli import cli
from .utils import *
from ..context import pass_context, Context, CONFIG_FILE, PrivacyPolicy, HUB_CONFIGS
from ..config import ConfigManager
from .component import Component, SPEC_FILE, ComponentAlreadyExistsException


def signal_handler(sig, frame):
    #print('You pressed Ctrl+C!')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def needs_credentials(f):
    @pass_context
    def run(ctx, *args, **kwargs):
        if ctx.SPLIGHT_ACCESS_ID is None or ctx.SPLIGHT_SECRET_KEY is None:
            click.secho(f"Please set your Splight credentials. Use \"splighthub configure\"", fg='red')
            exit(1)
        return f(ctx, *args, **kwargs)
    return update_wrapper(run, f)

logger = logging.getLogger()
NO_IMPORT_PWD_HASH = "b9d7c258fce446158f0ad1779c4bdfb14e35b6e3f4768b4e3b59297a48804bb15ba7d04c131d01841c55722416428c094beb83037bac949fa207af5c91590dbf"

@cli.command()
@click.argument("type", nargs=1, type=str)
@click.argument("name", nargs=1, type=str)
@click.argument("version", nargs=1, type=str)
@needs_credentials
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
        component = Component(path, context)
        component.create(name, type, version)
        click.secho(f"Component {name} created successfully in {path}", fg="green")

    except Exception as e:
        click.secho(f"Error creating component of type {type}: {str(e)}", fg="red")
        return


@cli.command()
@click.argument("type", nargs=1, type=str)
@click.argument("path", nargs=1, type=str)
@click.option("-f", "--force", is_flag=True, default=False, help="Force the component to be created even if it already exists.")
@click.option("-p", "--public", is_flag=True, default=False, help="Create a public component.")
@click.option("-ni", "--no-import", is_flag=True, default=False, help="Do not import component before pushing")
@needs_credentials
def push(context: Context, type: str, path: str, force: bool, public: bool, no_import: bool) -> None:
    """
    Push a component to the hub.\n
    Args:\n
        type: The type of the component.\n
        path: The path where the component is in local machine.\n
    """

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


@cli.command()
@click.argument("type", nargs=1, type=str)
@click.argument("name", nargs=1, type=str)
@click.argument("version", nargs=1, type=str)
@needs_credentials
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
        component = Component(path, context)
        component.pull(name, type, version)
        click.secho(f"Component {name}-{version} pulled successfully in {path}", fg="green")

    except Exception as e:
        click.secho(f"Error pulling component of type {type}: {str(e)}", fg="red")
        return


@cli.command()
@click.argument("component_type", nargs=1, type=str)
#@click.argument("token", nargs=1, type=str)
@needs_credentials
def list(context: Context, component_type: str) -> None:
    """
    List components of a given type.\n
    Args:\n
        component_type: The type of the component.\n
    """
    try:
        logger.setLevel(logging.WARNING)
        handler = ComponentHandler(context)
        list = handler.list_components(component_type)
        click.echo(json.dumps(list, indent=4))
        return list

    except Exception as e:
        click.secho(f"Error listing component of type {component_type}: {str(e)}", fg="red")
        return


@cli.command()
@click.argument("type", nargs=1, type=str)
@click.argument("path", nargs=1, type=str)
@click.argument("run_spec", nargs=1, type=str)
@needs_credentials
def run(context: Context, type: str, path: str, run_spec: str) -> None:
    """
    Run a component from the hub.\n
    Args:\n
        type: The type of the component.\n
        path: The path where the component is in local machine.\n
        run_spec: The run spec of the component.
    """
    try:
        component = Component(path, context)
        click.secho(f"Running component...", fg="green")
        component.run(type, run_spec)

    except Exception as e:
        click.secho(f"Error running component: {str(e)}", fg="red")
        return

@cli.command()
@click.argument("type", nargs=1, type=str)
@click.argument("path", nargs=1, type=str)
@needs_credentials
def test(context: Context, type: str, path: str) -> None:
    """
    Run a component from the hub.\n
    Args:\n
        type: The type of the component.\n
        path: The path where the component is in local machine.\n
    """
    try:
        component = Component(path, context)
        click.secho(f"Running component...", fg="green")
        component.test(type)

    except Exception as e:
        click.secho(f"Error running component: {str(e)}", fg="red")
        return

@cli.command()
@click.argument("type", nargs=1, type=str)
@click.argument("path", nargs=1, type=str)
@needs_credentials
def install_requirements(context: Context, type: str, path: str) -> None:
    """
    Run a component from the hub.\n
    Args:\n
        type: The type of the component.\n
        path: The path where the component is in local machine.\n
    """
    try:
        component = Component(path, context)
        click.secho(f"Installing component requirements...", fg="green")
        component.initialize()

    except Exception as e:
        click.secho(f"Error installing component requirements: {str(e)}", fg="red")
        return


@cli.command()
@pass_context
def configure(context: Context) -> None:
    """
    Configure Splight Hub.\n
    """
    try:
        # Precondition: Config file already exists
        # It is created when a command is run

        with open(CONFIG_FILE, 'r') as file:
            config_manager = ConfigManager(file)
            config = config_manager.load_config()

        for config_var in HUB_CONFIGS:
            old_value = config.get(config_var)
            hint = ' [' + old_value.replace(old_value[:-3], "*"*(len(old_value)-3)) + ']' if old_value is not None else ''

            if config_var == "SPLIGHT_HUB_API_HOST":
                if old_value is not None:
                    hint = f" [{old_value}]"
                else:
                    hint = f" [{SPLIGHT_HUB_API_HOST}]"
                    
            value = click.prompt(click.style(f"{config_var}{hint}", fg="yellow"), type=str, default="", show_default=False)
            if value != "":
                assert len(value) > 5 , f"{config_var} is too short"
                config[config_var] = value
            else:
                if config_var == "SPLIGHT_HUB_API_HOST" and old_value is None:
                    config[config_var] = SPLIGHT_HUB_API_HOST

        with open(CONFIG_FILE, 'w+') as file:
            config_manager = ConfigManager(file)
            config_manager.write_config(config)
        
        click.secho(f"Configuration saved successfully", fg="green")

    except Exception as e:
        click.secho(f"Error configuring Splight Hub: {str(e)}", fg="red")
        return