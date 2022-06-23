import click
import logging
from ..cli import workspace as workspace_cli
from ..utils import *
from ..context import Context, pass_context


logger = logging.getLogger()
logger.setLevel(logging.WARNING)

# TODO unify print in utils
def __print_results(items):
    for item in items:
        click.secho(item, fg='green' if '*' in item else 'white')


@workspace_cli.command()
@pass_context
def list(context: Context) -> None:
    try:
        results = context.list_workspaces()
        __print_results(results)
    except Exception as e:
        click.secho(f"Error configuring Splight Hub: {str(e)}", fg="red")
        return


@workspace_cli.command()
@click.argument("name", nargs=1, type=str)
@pass_context
def create(context: Context, name: str) -> None:
    try:
        context.create_workspace(name)
        results = context.list_workspaces()
        __print_results(results)
    except Exception as e:
        click.secho(f"Error configuring Splight Hub: {str(e)}", fg="red")
        return


@workspace_cli.command()
@click.argument("name", nargs=1, type=str)
@pass_context
def delete(context: Context, name: str) -> None:
    try:
        context.delete_workspace(name)
        click.secho(f"Deleted workspace {name}", fg="green")
    except Exception as e:
        click.secho(f"Error configuring Splight Hub: {str(e)}", fg="red")
        return


@workspace_cli.command()
@click.argument("name", nargs=1, type=str)
@pass_context
def select(context: Context, name: str) -> None:
    try:
        context.switch_workspace(name)
        results = context.list_workspaces()
        __print_results(results)
    except Exception as e:
        click.secho(f"Error configuring Splight Hub: {str(e)}", fg="red")
        return