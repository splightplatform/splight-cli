import click
import os
import pandas as pd
import logging
from splight_lib.database import DatabaseClient
from splight_lib.datalake import DatalakeClient, FakeDatalakeClient
from splight_lib.storage import StorageClient
import splight_models as models
from ..cli import datalake as datalake_cli
from .datalake import Datalake
from ..utils import *
from ..context import Context, pass_context


logger = logging.getLogger()
logger.setLevel(logging.WARNING)

#TODO: currently only working for datalake
@datalake_cli.command()
@click.argument("collection", nargs=1, type=str)
@click.argument("path", nargs=1, type=str)
@click.option('--namespace', '-n', help="Namespace of the resource")
@pass_context
def load(context: Context, collection: str, path: str, namespace: str=None) -> None:
    """
    Load data into Splight.\n
    Args:\n
        collection: Name of the datalake collection.\n
        path: Path to csv containing data to be loaded.\n
    """
    try:
        user_handler = UserHandler(context)

        if not namespace:
            namespace = user_handler.user_namespace

        datalake = Datalake(context, namespace)
        datalake.load(collection, path)

    except Exception as e:
        click.echo(f"Error loading data: {str(e)}")
        return

#TODO: currently only working for datalake
@datalake_cli.command()
@click.argument("path", nargs=1, type=str)
@click.argument("collection", nargs=1, type=str, required=False)
@click.option('--filter', '-f', multiple=True, default=[], help="Filters (should be in the form of key=value)")
@click.option('--namespace', '-n', help="Namespace of the resource")
@click.option('--remote', '-r', is_flag=True, help="Dump from remote datalake")
@click.option('--example', '-e', is_flag=True, help="Dump template data")
@pass_context
def dump(context: Context, path: str, collection: str, filter: list, namespace: str=None, remote: bool=None, example: bool = False) -> None:
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