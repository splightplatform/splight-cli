import click
import logging
from cli.cli import database as database_cli
from cli.database.database import Database
from cli.utils import *
from cli.context import Context, pass_context


logger = logging.getLogger()


@database_cli.command()
@click.argument('obj_class')
@pass_context
def list(context: Context, obj_class: str) -> None:
    try:
        database = Database(context)
        items = database.list(obj_class)
        Printer.print_dict(items=items, headers=['id', 'name'])

    except Exception as e:
        click.secho(f"Error listing database: {str(e)}", fg="red")
        return