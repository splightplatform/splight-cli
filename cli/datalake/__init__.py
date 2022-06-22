import click
import logging
from ..cli import datalake as datalake_cli
from .datalake import Datalake
from ..utils import *
from ..context import Context, pass_context


logger = logging.getLogger()
logger.setLevel(logging.WARNING)

@datalake_cli.command()
@click.argument("collection", nargs=1, type=str)
@click.option("--path", '-p', nargs=1, type=str, help="Path to csv file to be loaded")
@click.option('--namespace', '-n', help="Namespace of the resource")
@click.option('--remote', '-r', is_flag=True, help="Load to remote datalake")
@click.option('--example', '-e', is_flag=True, help="Dump template data")
@pass_context
def load(context: Context, collection: str, path: str=None, namespace: str=None, example: bool=None, remote: bool=None) -> None:
    """
    Load data into Splight.\n
    Args:\n
        collection: Name of the datalake collection.\n
    """
    try:
        user_handler = UserHandler(context)
        if example and namespace:
            raise Exception("Cannot specify namespace when dumping example data")
        if example and path:
            raise Exception("Cannot specify path when dumping example data")
        if not example and not path:
            raise Exception("Must specify path to csv file when not dumping example data")

        if not namespace:
            namespace = user_handler.user_namespace

        datalake = Datalake(context, namespace)
        datalake.load(collection, path, example, remote)

    except Exception as e:
        click.echo(f"Error loading data: {str(e)}")
        return

@datalake_cli.command()
@click.argument("collection", nargs=1, type=str, required=False)
@click.option('--filter', '-f', multiple=True, default=[], help="Filters (should be in the form of key=value)")
@click.option("--path", '-p', nargs=1, type=str, default='.')
@click.option('--namespace', '-n', help="Namespace of the resource")
@click.option('--remote', '-r', is_flag=True, help="Dump from remote datalake")
@click.option('--example', '-e', is_flag=True, help="Dump template data")
@pass_context
def dump(context: Context, collection: str, path: str, filter: list, namespace: str=None, remote: bool=None, example: bool = False) -> None:
    """
    Dump data from Splight.\n
    Args:\n
        collection: Name of the datalake collection.\n
        path: Path to csv where dump data will be stored.\n
    """
    try:
        if not example:
            if collection is None:
                raise Exception("missing argument COLLECTION")
        user_handler = UserHandler(context)
        if example and namespace:
            raise Exception("Cannot specify namespace when dumping example data")
        if not namespace:
            namespace = user_handler.user_namespace
        datalake = Datalake(context, namespace)
        datalake.dump(collection, path, filter, remote, example)

    except Exception as e:
        click.secho(f"Error dumping data: {str(e)}", fg="red")
        return

@datalake_cli.command()
@click.option('--namespace', '-n', help="Namespace of the resource")
@click.option('--remote', '-r', is_flag=True, help="Show collections in remote datalake")
@needs_credentials
def list(context: Context, namespace: str=None, remote: bool=None) -> None:
    """
    List datalake collections \n
    """
    try:
        user_handler = UserHandler(context)
        if not namespace:
            namespace = user_handler.user_namespace

        datalake = Datalake(context, namespace)
        datalake.list(remote)

        return list

    except Exception as e:
        click.secho(f"Error listing datalake: {str(e)}", fg="red")
        return