import click
import os
import pandas as pd
from cli import cli
from cli.context import Context, pass_context
from splight_lib.database import DatabaseClient, Attribute
from splight_lib.datalake import DatalakeClient
from splight_lib.storage import StorageClient
from splight_lib.communication import Variable
import splight_models as models

VALID_CLIENTS = [
    "database",
    "datalake",
    "storage"
]

CLASS_MAP = {
    "database": DatabaseClient,
    "datalake": DatalakeClient,
    "storage": StorageClient
}

@cli.command()
@click.argument("target", type=click.Choice(VALID_CLIENTS, case_sensitive=False))
@click.argument("type", nargs=1, type=str)
@click.argument("path", nargs=1, type=str)
@pass_context
def load_data(context: Context, target: str, type: str, path: str) -> None:
    """
    Load data into Splight.\n
    Args:\n
        target: The target where the data will be loaded.\n
        type: The type of the data.\n
        path: The data to be loaded.
    """
    try:
        client = CLASS_MAP[target](context.namespace)
        type = getattr(models, type)
        if not os.path.isfile(path):
            raise Exception("File not found")
        if not path.endswith(".csv"):
            raise Exception("Only CSV files are supported")

        # TODO: Support this for things different than Variables
        client.save_dataframe(pd.read_csv(path))

    except Exception as e:
        click.echo(f"Error loading data: {str(e)}")
        return

@cli.command()
@click.argument("target", type=click.Choice(VALID_CLIENTS, case_sensitive=False))
@click.argument("type", nargs=1, type=str)
@click.argument("path", nargs=1, type=str)
@pass_context
def dump_data(context: Context, source: str, type: str, path: str) -> None:
    """
    Dump data from Splight.\n
    Args:\n
        source: The source from where the data will be read.\n
        type: The type of the data.\n
        path: The path where the data will be saved.
    """
    try:
        client = CLASS_MAP[source](context.namespace)
        type = getattr(models, type)
        if not os.path.isdir(path):
            raise Exception("Directory not found")

        #TODO: Support this for database or things that are not Variables
        data = client.get_dataframe()
        data.to_csv(path)

    except Exception as e:
        click.echo(f"Error dumping data: {str(e)}")
        return
