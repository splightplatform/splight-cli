import json
from typing import List, Optional

import typer
from rich.console import Console
from splight_lib.models import Component

from splight_cli.constants import error_style, success_style
from splight_cli.engine.manager import (
    ComponentUpgradeManager,
    ComponentUpgradeManagerException,
    ResourceManager,
    ResourceManagerException,
)

component_app = typer.Typer(
    name="Splight Engine Component",
    add_completion=True,
    rich_markup_mode="rich",
    no_args_is_help=True,
)

console = Console()
MODEL = Component


@component_app.command()
def list(
    ctx: typer.Context,
    filters: Optional[List[str]] = typer.Option(
        None,
        "--filter",
        "-f",
        help="Query param in the form key=value",
    ),
):
    manager = ResourceManager(
        model=MODEL,
    )
    params = manager.get_query_params(filters)
    manager.list(params=params)


@component_app.command()
def get(
    ctx: typer.Context,
    instance_id: str = typer.Argument(..., help="The Asset's ID"),
):
    manager = ResourceManager(
        model=MODEL,
    )
    try:
        manager.get(instance_id)
    except ResourceManagerException as exc:
        console.print(exc, style=error_style)


@component_app.command()
def create(
    ctx: typer.Context,
    path: str = typer.Argument(
        ..., help="Path to JSON file with resource data"
    ),
):
    manager = ResourceManager(
        model=MODEL,
    )
    with open(path, "r") as fid:
        body = json.load(fid)
    manager.create(data=body)


@component_app.command()
def upgrade(
    context: typer.Context,
    from_component_id: str = typer.Argument(
        ..., help="The ID of the component to be upgraded"
    ),
    version: str = typer.Option(
        ...,
        "--version",
        "-v",
        help="The version of the HubComponent to be upgraded to",
    ),
):
    """Upgrade a component to a new version of its HubComponent."""

    manager = ComponentUpgradeManager(component_id=from_component_id)

    try:
        new_component = manager.upgrade(version)
    except ComponentUpgradeManagerException as exc:
        console.print(exc, style=error_style)
        raise typer.Exit(code=1)

    console.print(
        f"New component name: {new_component.name}, id: {new_component.id}",
        style=success_style,
    )


@component_app.command()
def clone(
    context: typer.Context,
    from_component_id: str = typer.Argument(
        ..., help="The ID of the component to be upgraded"
    ),
    version: Optional[str] = typer.Option(
        None,
        "--version",
        "-v",
        help="The version of the HubComponent to be upgraded to",
    ),
):
    """Creates a new component from an existing component in the engine. If the
    version parameter is used it also updates the version of the Hub Component
    used.
    """
    manager = ComponentUpgradeManager(component_id=from_component_id)

    try:
        new_component = manager.clone_component(version)
    except ComponentUpgradeManagerException as exc:
        console.print(exc, style=error_style)
        raise typer.Exit(code=1)

    console.print(
        f"New component name: {new_component.name}, id: {new_component.id}",
        style=success_style,
    )


@component_app.command()
def delete(
    ctx: typer.Context,
    instance_id: str = typer.Argument(
        ..., help="The ID of the instance to be removed"
    ),
):
    manager = ResourceManager(
        model=MODEL,
    )
    manager.delete(instance_id)


@component_app.command()
def download(
    ctx: typer.Context,
    instance_id: str = typer.Argument(
        ..., help="The ID of the instance to download"
    ),
    path: str = typer.Option(".", help="Path to download file"),
):
    manager = ResourceManager(
        model=MODEL,
    )
    manager.download(instance_id, path=path)
