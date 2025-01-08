import typer
from rich.console import Console
from splight_lib.models import Component

from splight_cli.constants import error_style
from splight_cli.hub.component.hub_manager import HubComponentManager

component_app = typer.Typer(
    name="Splight Hub Component",
    add_completion=True,
    rich_markup_mode="rich",
    no_args_is_help=True,
)

console = Console()
MODEL = Component


@component_app.command()
def list(ctx: typer.Context):
    try:
        manager = HubComponentManager()
        manager.list_components()
    except Exception as exc:
        console.print(f"Error listing components: {exc}", style=error_style)
        raise typer.Exit(code=1)


@component_app.command()
def versions(
    ctx: typer.Context, name: str = typer.Argument(..., help="Componet's name")
):
    try:
        manager = HubComponentManager()
        manager.versions(name=name)
    except Exception as exc:
        console.print(
            f"Error getting component versions: {exc}", style=error_style
        )
        raise typer.Exit(code=1)
