from unittest import result
import click
import logging
from ..cli import storage as storage_cli
from .storage import Storage
from ..utils import *
from ..context import Context


logger = logging.getLogger()
logger.setLevel(logging.WARNING)


def __print_results(headers, items):
    click.secho('\t'.join([h.upper() for h in headers]))
    for item in items:
        click.secho('\t'.join([getattr(item, key) for key in headers]))


@storage_cli.command()
@click.option('--namespace', '-n', help="Namespace of the resource")
@needs_credentials
def list(context: Context, namespace: str=None) -> None:
    """
    List storage items \n
    """
    try:
        user_handler = UserHandler(context)
        if not namespace:
            namespace = user_handler.user_namespace

        storage = Storage(context, namespace)
        
        results = storage.get()
        __print_results(headers=["id"], items=results)


    except Exception as e:
        click.secho(f"Error listing storage: {str(e)}", fg="red")


@storage_cli.command()
@click.argument("file", nargs=1, type=str)
@click.option('--namespace', '-n', help="Namespace of the resource")
@needs_credentials
def load(context: Context, file: str, namespace: str=None) -> None:
    """
    Load storage item \n
    """
    try:
        user_handler = UserHandler(context)
        if not namespace:
            namespace = user_handler.user_namespace

        storage = Storage(context, namespace)
        storage.save(file)

    except Exception as e:
        logger.exception(e)
        click.secho(f"Error laoding storage: {str(e)}", fg="red")


@storage_cli.command()
@click.argument("file", nargs=1, type=str)
@click.option('--namespace', '-n', help="Namespace of the resource")
@needs_credentials
def delete(context: Context, file: str, namespace: str=None) -> None:
    """
    Delete storage item \n
    """
    try:
        user_handler = UserHandler(context)
        if not namespace:
            namespace = user_handler.user_namespace

        storage = Storage(context, namespace)
        storage.delete(file)

    except Exception as e:
        logger.exception(e)
        click.secho(f"Error deleting storage: {str(e)}", fg="red")