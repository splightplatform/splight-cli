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
def list(ctx: typer.Context):
    try:
        manager = HubServerManager()
        manager.list_servers()
    except Exception as exc:
        console.print(f"Error listing servers: {exc}", style=error_style)
        raise typer.Exit(code=1)
