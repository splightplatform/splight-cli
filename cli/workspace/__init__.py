import click
import logging

from cli.utils.pprint import Printer
from cli.cli import workspace as workspace_cli
from cli.utils import *
from cli.context import Context, pass_context


logger = logging.getLogger()

@workspace_cli.command()
@pass_context
def list(context: Context) -> None:
    try:
        results = context.workspace.list_workspaces()
        results_colors = ['green' if '*' in item else Printer.DEFAULT_COLOR for item in results]
        Printer.print_list(items=results, items_colors=results_colors, header="WORKSPACES")
    except Exception as e:
        click.secho(f"Error configuring Splight Hub: {str(e)}", fg="red")
        return


@workspace_cli.command()
@click.argument("name", nargs=1, type=str)
@pass_context
def create(context: Context, name: str) -> None:
    try:
        context.workspace.create_workspace(name)
        results = context.workspace.list_workspaces()
        results_colors = ['green' if '*' in item else Printer.DEFAULT_COLOR for item in results]
        Printer.print_list(items=results, items_colors=results_colors, header="WORKSPACES")
    except Exception as e:
        click.secho(f"Error configuring Splight Hub: {str(e)}", fg="red")
        return


@workspace_cli.command()
@click.argument("name", nargs=1, type=str)
@pass_context
def delete(context: Context, name: str) -> None:
    try:
        context.workspace.delete_workspace(name)
        click.secho(f"Deleted workspace {name}", fg="green")
    except Exception as e:
        click.secho(e, fg="red")
        return


@workspace_cli.command()
@click.argument("name", nargs=1, type=str)
@pass_context
def select(context: Context, name: str) -> None:
    try:
        context.workspace.select_workspace(name)
        click.secho(f"Current workspace: {name}", fg="green")
    except Exception as e:
        click.secho(f"Error configuring Splight Hub: {str(e)}", fg="red")
        return
