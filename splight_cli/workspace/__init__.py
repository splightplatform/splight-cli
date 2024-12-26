from functools import wraps

import typer
from rich.console import Console
from rich.table import Table
from splight_lib.config import SplightConfigManager

from splight_cli.constants import error_style, success_style

console = Console()

workspace_app = typer.Typer(
    name="Splight CLI Workspace",
    add_completion=True,
    rich_markup_mode="rich",
)


def display_workspaces(workspaces: list[str], current: str) -> None:
    table = Table("Workspaces", show_lines=False, show_edge=False)
    for item in workspaces:
        style = success_style if item == current else None
        table.add_row(item, style=style)
    console.print(table)


def error_handler(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            console.print(str(e), style=error_style)
            raise typer.Exit(code=1)

    return wrapper


@workspace_app.command()
@error_handler
def list() -> None:
    config = SplightConfigManager()
    display_workspaces(config.list(), config.current)


@workspace_app.command()
@error_handler
def create(
    name: str = typer.Argument(..., help="The workspace's name"),
) -> None:
    config = SplightConfigManager()
    config.create(name)
    display_workspaces(config.list(), config.current)


@workspace_app.command()
@error_handler
def delete(
    name: str = typer.Argument(..., help="The workspace's name"),
) -> None:
    config = SplightConfigManager()
    config.delete(name)
    console.print(f"Deleted workspace {name}", style=success_style)


@workspace_app.command()
@error_handler
def select(
    name: str = typer.Argument(..., help="The workspace's name"),
) -> None:
    config = SplightConfigManager()
    config.set_current(name)
    console.print(f"Current workspace: {name}", style=success_style)
