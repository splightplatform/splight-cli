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
logger.setLevel(logging.WARNING)

#TODO: currently only working for datalake
@cli.command()
@click.argument("resource", type=click.Choice(VALID_CLIENTS, case_sensitive=False))
@click.argument("collection", nargs=1, type=str)
@click.argument("path", nargs=1, type=str)
@click.option('--namespace', '-n', help="Namespace of the resource")
@pass_context
def load(context: Context, resource: str, collection: str, path: str, namespace: str=None) -> None:
    """
    Load data into Splight.\n
    Args:\n
        resource: The resource where the data will be loaded. (currently only datalake supported)\n
        collection: Name of the datalake collection.\n
        path: Path to csv containing data to be loaded.\n
    """
    try:
        if not namespace:
            namespace = 'splight'
        client = CLASS_MAP[resource](namespace)
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
@click.option('--namespace', '-n', help="Namespace of the resource")
@click.option('--example', '-e', is_flag=True, help="Dump template data")
@click.option('--filter', '-f', multiple=True, help="Filters (should be in the form of key=value)")
@pass_context
def dump(context: Context, resource: str, collection: str, path: str, namespace: str=None, example: bool = False, filter: list=None) -> None:
    """
    Dump data from Splight.\n
    Args:\n
        resource: The resource where the data will be dumped. (currently only datalake supported)\n
        collection: Name of the datalake collection.\n
        path: Path to csv where dump data will be stored.\n
    """
    try:
        if os.path.isdir(path):
            path = os.path.join(path, 'splight_dump.csv')
        elif not path.endswith(".csv"):
            raise Exception("Only CSV files are supported")

        if example and namespace:
            raise Exception("Cannot specify namespace when dumping example data")
        if example:
            with open(f"{BASE_DIR}/playground/dump_example.csv", 'rb') as f:
                ff = open(path, 'wb+')
                ff.write(f.read())
                ff.close()
                return
        if not namespace:
            namespace = 'splight'
        
        client = CLASS_MAP[resource](namespace)
        filters = {f.split('=')[0]: f.split('=')[1] for f in filter}
        # TODO: Support this for things different than Variables
        client.get_dataframe(resource_type=models.Variable,
                             collection=collection,
                             limit_=0,
                             **filters).to_csv(path)

    except Exception as e:
        click.secho(f"Error dumping data: {str(e)}", fg="red")
        return

@cli.command()
@click.argument("resource_type", nargs=1, type=str)
@click.option('--namespace', '-n', help="Namespace of the resource")
@click.option('--remote', '-r', is_flag=True, help="Show collections in remote datalake")
@needs_credentials
def show(context: Context, resource_type: str, namespace: str=None, remote: bool=None) -> None:
    """
    List resource of a given type.\n
    Args:\n
        resource_type: Resource to be listed. (currently only datalake supported)\n
    """
    resource_content = {
        'datalake': "collections"
    }

    if not namespace:
        namespace = 'splight'
    try:
        logger.setLevel(logging.WARNING)
        client = CLASS_MAP[resource_type](namespace)
        if remote:
            handler = RemoteDatalakeHandler(context)
            collections = handler.list_source()
        else:
            collections = [{"source": col, "algo": "-"} for col in client.list_collection_names()]

        click.secho("{:<50} {:<15}".format('COLLECTION', 'ALGORITHM'))
        for collection in collections:
            click.secho("{:<50} {:<15}".format(collection['source'], collection['algo']))
        return list

    except Exception as e:
        click.secho(f"Error listing component of type {resource_type}: {str(e)}", fg="red")
        return

@cli.command()
@click.argument("resource", type=click.Choice(VALID_CLIENTS, case_sensitive=False))
@click.argument("collection", nargs=1, type=str)
@click.argument("path", nargs=1, type=str)
@click.option('--filter', '-f', multiple=True, help="Filters")
@pass_context
def downloaddata(context: Context, resource: str, collection: str, path: str, filter: list=None) -> None:
    """
    Download data from Splight remote.\n
    Args:\n
        resource: The resource where the data will be dumped. (currently only datalake supported)\n
        collection: Name of the datalake collection.\n
        path: Path to csv where dump data will be stored.\n
    """
    try:
        if os.path.isdir(path):
            path = os.path.join(path, 'splight_dump.csv')
        elif not path.endswith(".csv"):
            raise Exception("Only CSV files are supported")

        handler = RemoteDatalakeHandler(context)
        filters = {f.split('=')[0]: f.split('=')[1] for f in filter}
        filters['source'] = collection
        if 'limit_' not in filters:
            filters['limit_'] = 0

        handler.dump(path, filters)   

    except Exception as e:
        click.secho(f"Error dumping data: {str(e)}", fg="red")
        return