import click
import logging
from cli.cli import datalake as datalake_cli
from cli.datalake.datalake import Datalake
from cli.utils import *
from cli.context import Context, pass_context


logger = logging.getLogger()


@datalake_cli.command()
@click.option("--collection", '-c', nargs=1, type=str, help="Collection where to load data")
@click.option("--path", '-p', nargs=1, type=str, help="Path to csv file to be loaded")
@click.option('--example', '-e', is_flag=True, help="Dump template data")
@pass_context
def load(context: Context, collection: str=None, path: str=None, example: bool=None) -> None:
    try:
        if not collection:
            collection = 'default'

        datalake = Datalake(context)
        datalake.load(collection, path, example)

    except Exception as e:
        logger.exception(e)
        click.echo(f"Error loading data: {str(e)}")
        return

@datalake_cli.command()
@click.option("--collection", '-c', nargs=1, type=str, help="Collection where to dump data")
@click.option('--filter', '-f', multiple=True, default=[], help="Filters (should be in the form of key=value)")
@click.option("--path", '-p', nargs=1, type=str, default='.')
@click.option('--example', '-e', is_flag=True, help="Dump template data")
@pass_context
def dump(context: Context, collection: str, path: str, filter: list, example: bool = False) -> None:
    try:
        if not collection:
            collection = 'default'
        datalake = Datalake(context)
        datalake.dump(collection, path, filter, example)
    except Exception as e:
        logger.exception(e)
        click.secho(f"Error dumping data: {str(e)}", fg="red")
        return

@datalake_cli.command()
@pass_context
def list(context: Context) -> None:
    try:
        datalake = Datalake(context)
        collections = datalake.list()
        Printer.print_list(items=collections, header='collection_name')

    except Exception as e:
        click.secho(f"Error listing datalake: {str(e)}", fg="red")
        return