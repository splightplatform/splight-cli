import click
import logging
from ..cli import datalake as datalake_cli
from .datalake import Datalake
from ..utils import *
from ..auth import needs_credentials
from ..context import Context


logger = logging.getLogger()
logger.setLevel(logging.WARNING)


@datalake_cli.command()
@click.option("--collection", '-c', nargs=1, type=str, help="Collection where to load data")
@click.option("--path", '-p', nargs=1, type=str, help="Path to csv file to be loaded")
@click.option('--namespace', '-n', help="Namespace of the resource")
@click.option('--remote', '-r', is_flag=True, help="Load to remote datalake")
@click.option('--example', '-e', is_flag=True, help="Dump template data")
@needs_credentials
def load(context: Context, collection: str=None, path: str=None, namespace: str=None, example: bool=None, remote: bool=None) -> None:
    try:
        user_handler = UserHandler(context)
        if not namespace and remote:
            namespace = user_handler.user_namespace

        if not collection:
            collection = 'default'

        datalake = Datalake(context, namespace)
        datalake.load(collection, path, example, remote)

    except Exception as e:
        logger.exception(e)
        click.echo(f"Error loading data: {str(e)}")
        return

@datalake_cli.command()
@click.option("--collection", '-c', nargs=1, type=str, help="Collection where to dump data")
@click.option('--filter', '-f', multiple=True, default=[], help="Filters (should be in the form of key=value)")
@click.option("--path", '-p', nargs=1, type=str, default='.')
@click.option('--namespace', '-n', help="Namespace of the resource")
@click.option('--remote', '-r', is_flag=True, help="Dump from remote datalake")
@click.option('--example', '-e', is_flag=True, help="Dump template data")
@needs_credentials
def dump(context: Context, collection: str, path: str, filter: list, namespace: str=None, remote: bool=None, example: bool = False) -> None:
    try:
        user_handler = UserHandler(context)
        if not namespace and remote:
            namespace = user_handler.user_namespace
        if not collection:
            collection = 'default'
        datalake = Datalake(context, namespace)
        datalake.dump(collection, path, filter, remote, example)

    except Exception as e:
        logger.exception(e)
        click.secho(f"Error dumping data: {str(e)}", fg="red")
        return

@datalake_cli.command()
@click.option('--namespace', '-n', help="Namespace of the resource")
@click.option('--remote', '-r', is_flag=True, help="Show collections in remote datalake")
@needs_credentials
def list(context: Context, namespace: str=None, remote: bool=None) -> None:
    try:
        user_handler = UserHandler(context)
        if not namespace and remote:
            namespace = user_handler.user_namespace

        datalake = Datalake(context, namespace)
        collections = datalake.list(remote)
        Printer.print_dict(items=collections, headers=['collection', 'algorithm'])

    except Exception as e:
        click.secho(f"Error listing datalake: {str(e)}", fg="red")
        return