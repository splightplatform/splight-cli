import click
import logging
from ..cli import history as history_cli
from .history import History
from ..utils import *
from ..auth import needs_credentials
from ..context import Context


logger = logging.getLogger()
logger.setLevel(logging.WARNING)


@history_cli.command()
@click.argument("file", nargs=1, type=str)
@click.option('--asset-id', nargs=1, help="Fixed asset id")
@click.option('--asset-col', multiple=True, default=[], help="Asset name by columns")
@click.option('--attribute-id', nargs=1, help="Fixed attribute id")
@click.option('--attribute-col', multiple=True, default=[], help="Attribute name by columns")
@click.option('--namespace', '-n', help="Namespace of the resource")
@click.option('--remote', '-r', is_flag=True, help="Load to remote shortcut")
@click.option('--example', '-e', is_flag=True, help="Dump template data")
@needs_credentials
def load(context: Context,
                       asset_id: str = None,
                       asset_col: str = [],
                       attribute_id: str = None,
                       attribute_col: str = [],
                       file: str = None,
                       namespace: str = None,
                       example: bool = None,
                       remote: bool = None) -> None:
    try:
        user_handler = UserHandler(context)
        if not namespace and remote:
            namespace = user_handler.user_namespace

        if not asset_col and not asset_id:
            raise Exception(f"You should enter one of asset_col, asset_id")

        if not attribute_col and not attribute_id:
            raise Exception(f"You should enter one of attribute_col, attribute_id")

        attribute_cols = list(attribute_col)
        asset_cols = list(asset_col)
        handler = History(context, namespace)
        handler.load(asset_id, asset_cols, attribute_id, attribute_cols, file, example, remote)
        click.secho(f"Succesfully loaded data.", fg="green")
    except Exception as e:
        click.secho(f"Error loading data: {str(e)}", fg='red')
        return
