import click
import os
import pandas as pd
import logging
from splight_lib.database import DatabaseClient
from splight_lib.datalake import DatalakeClient, FakeDatalakeClient
from splight_lib.storage import StorageClient
import splight_models as models
from ..cli import cli
from ..hub.utils import *
from ..context import Context, pass_context

VALID_CLIENTS = [
    # "database",
    "datalake",
    # "storage"
]

FAKE_CLASS_MAP = {
    # "database": DatabaseClient,
    "datalake": FakeDatalakeClient,
    # "storage": StorageClient
}

CLASS_MAP = {
    # "database": DatabaseClient,
    "datalake": DatalakeClient,
    # "storage": StorageClient
}

logger = logging.getLogger()

#TODO: currently only working for datalake
@cli.command()
@click.argument("resource", type=click.Choice(VALID_CLIENTS, case_sensitive=False))
@click.argument("collection", nargs=1, type=str)
@click.argument("path", nargs=1, type=str)
@pass_context
def load(context: Context, resource: str, collection: str, path: str) -> None:
    """
    Load data into Splight.\n
    Args:\n
        resource: The resource where the data will be loaded.\n
        type: The type of the data.\n
        path: The data to be loaded.
    """
    try:
        client = FAKE_CLASS_MAP[resource]('splight')
        if not os.path.isfile(path):
            raise Exception("File not found")
        if not path.endswith(".csv"):
            raise Exception("Only CSV files are supported")
        # TODO: Support this for things different than Variables
        client.save_dataframe(pd.read_csv(path), collection=collection)

    except Exception as e:
        click.echo(f"Error loading data: {str(e)}")
        return

#TODO: currently only working for datalake
@cli.command()
@click.argument("resource", type=click.Choice(VALID_CLIENTS, case_sensitive=False))
@click.argument("collection", nargs=1, type=str)
@click.argument("path", nargs=1, type=str)
@pass_context
def dump(context: Context, resource: str, collection: str, path: str) -> None:
    """
    Dump data from Splight.\n
    Args:\n
        source: The source from where the data will be read.\n
        type: The type of the data.\n
        path: The path where the data will be saved.
    """
    try:
        
        handler = DatalakeHandler(context)
        handler.dump(collection, path)

    except Exception as e:
        click.echo(f"Error dumping data: {str(e)}")
        return

@cli.command()
@click.argument("resource_type", nargs=1, type=str)
@needs_credentials
def show(context: Context, resource_type: str) -> None:
    """
    List resource of a given type.\n
    Args:\n
        resource_type: The type of the component.\n
    """
    resource_content = {
        'datalake': "collections"
    }
    try:
        logger.setLevel(logging.WARNING)
        handler = DatalakeHandler(context)
        content = {}
        click.secho("{:<50} {:<10}".format('COLLECTION','ALGORITHM'))
        for collection in handler.list_source():
            click.secho("{:<50} {:<10}".format(collection['source'], collection['algo']))
        return list

    except Exception as e:
        click.secho(f"Error listing component of type {resource_type}: {str(e)}", fg="red")
        return

# @cli.command()
# @click.argument("type", nargs=1, type=str)
# @click.argument("name", nargs=1, type=str)
# @click.argument("version", nargs=1, type=str)
# @needs_credentials
# def load(context: Context, type: str, name: str, version: str) -> None:
#     """
#     Pull a component from the hub.\n
#     Args:\n
#         type: The type of the component.\n
# @cli.command()
#         path = os.path.abspath(".")
#         component = Component(path, context)
#         component.pull(name, type, version)
#         click.secho(f"Component {name}-{version} pulled successfully in {path}", fg="green")

#     except Exception as e:
#         click.secho(f"Error pulling component of type {type}: {str(e)}", fg="red")
#         return