import click
import logging
from ..cli import database as database_cli
from .database import Database
from ..utils import *
from ..auth import needs_credentials
from ..context import Context


logger = logging.getLogger()
logger.setLevel(logging.WARNING)


@database_cli.command()
@click.argument('obj_class')
@click.option('--namespace', '-n', help="Namespace of the resource")
@click.option('--remote', '-r', is_flag=True, help="Show objects in remote datalake")
@needs_credentials
def list(context: Context, obj_class: str, namespace: str=None, remote: bool=None) -> None:
    try:
        user_handler = UserHandler(context)
        if not namespace and remote:
            namespace = user_handler.user_namespace

        database = Database(context, namespace)
        items = database.list(obj_class, remote=remote)
        Printer.print_dict(items=items, headers=['id', 'name'])

    except Exception as e:
        click.secho(f"Error listing database: {str(e)}", fg="red")
        return