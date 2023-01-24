# import json

import typer
from rich.console import Console
from splight_models import Component

from cli.hub.component.hub_manager import HubComponentManager

# from cli.constants import error_style

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
    manager = HubComponentManager(client=ctx.obj.framework.setup.HUB_CLIENT())
    manager.push(path, force=force)


@component_app.command()
def pull(
    ctx: typer.Context,
    name: str = typer.Argument(..., help="The component's name"),
    version: str = typer.Argument(..., help="The component's version"),
):
    manager = HubComponentManager(client=ctx.obj.framework.setup.HUB_CLIENT())
    manager.pull(name=name, version=version)


@component_app.command()
def delete(
    ctx: typer.Context,
    name: str = typer.Argument(..., help="Component's name"),
    version: str = typer.Argument(..., help="Component's version"),
):
    manager = HubComponentManager(client=ctx.obj.framework.setup.HUB_CLIENT())
    manager.delete(name, version)


@component_app.command()
def list(ctx: typer.Context):
    manager = HubComponentManager(client=ctx.obj.framework.setup.HUB_CLIENT())
    manager.list_components()


@component_app.command()
def versions(
    ctx: typer.Context, name: str = typer.Argument(..., help="Componet's name")
):
    manager = HubComponentManager(client=ctx.obj.framework.setup.HUB_CLIENT())
    manager.versions(name=name)
