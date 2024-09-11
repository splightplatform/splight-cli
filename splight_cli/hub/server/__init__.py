import typer
from rich.console import Console
from splight_lib.models import Component

from splight_cli.constants import error_style
from splight_cli.hub.server.server_manager import HubServerManager

server_app = typer.Typer(
    name="Splight Hub Server",
    add_completion=True,
    rich_markup_mode="rich",
    no_args_is_help=True,
)

console = Console()
MODEL = Component


@server_app.command()
def push(
    ctx: typer.Context,
    path: str = typer.Argument(..., help="Path to server files"),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Overwrite existing server in Splight HUB",
    ),
):
    try:
        manager = HubServerManager()
        manager.push(path, force=force)
    except Exception as exc:
        console.print(f"Error pushing server: {exc}", style=error_style)
        raise
        raise typer.Exit(code=1)


@server_app.command()
def pull(
    ctx: typer.Context,
    name: str = typer.Argument(..., help="The servers's name"),
    version: str = typer.Argument(..., help="The servers's version"),
):
    try:
        manager = HubServerManager()
        manager.pull(name=name, version=version)
    except Exception as exc:
        console.print(f"Error pulling server: {exc}", style=error_style)
        raise typer.Exit(code=1)


@server_app.command()
def list(ctx: typer.Context):
    try:
        manager = HubServerManager()
        manager.list_servers()
    except Exception as exc:
        console.print(f"Error listing servers: {exc}", style=error_style)
        raise typer.Exit(code=1)
