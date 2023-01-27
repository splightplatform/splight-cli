import typer
from rich.console import Console
from splight_models import Component

from cli.constants import error_style
from cli.hub.component.hub_manager import HubComponentManager

component_app = typer.Typer(
    name="Splight Engine Component",
    add_completion=True,
    rich_markup_mode="rich",
    no_args_is_help=True,
)

console = Console()
MODEL = Component


@component_app.command()
def push(
    ctx: typer.Context,
    path: str = typer.Argument(..., help="Path to component source code"),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Overwrite existing component in Splight HUB",
    ),
):
    try:
        manager = HubComponentManager(
            client=ctx.obj.framework.setup.HUB_CLIENT()
        )
        manager.push(path, force=force)
    except Exception as exc:
        console.print(f"Error pushing component {exc}", style=error_style)
        raise typer.Exit(1)


@component_app.command()
def pull(
    ctx: typer.Context,
    name: str = typer.Argument(..., help="The component's name"),
    version: str = typer.Argument(..., help="The component's version"),
):
    try:
        manager = HubComponentManager(
            client=ctx.obj.framework.setup.HUB_CLIENT()
        )
        manager.pull(name=name, version=version)
    except Exception as exc:
        console.print(f"Error pulling component {exc}", style=error_style)
        raise typer.Exit(1)


@component_app.command()
def list(ctx: typer.Context):
    try:
        manager = HubComponentManager(
            client=ctx.obj.framework.setup.HUB_CLIENT()
        )
        manager.list_components()
    except Exception as exc:
        console.print(f"Error listing components {exc}", style=error_style)
        raise typer.Exit(1)


@component_app.command()
def versions(
    ctx: typer.Context, name: str = typer.Argument(..., help="Componet's name")
):
    try:
        manager = HubComponentManager(
            client=ctx.obj.framework.setup.HUB_CLIENT()
        )
        manager.versions(name=name)
    except Exception as exc:
        console.print(
            f"Error showing component's version {exc}", style=error_style
        )
        raise typer.Exit(1)
