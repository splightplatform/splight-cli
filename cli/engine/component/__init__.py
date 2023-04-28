import json
from typing import List, Optional

import typer
from rich.console import Console
from splight_models import (
    Component,
)

from cli.constants import error_style
from cli.engine.manager import ResourceManager, ResourceManagerException, ComponentUpgradeManager


component_app = typer.Typer(
    name="Splight Engine Component",
    add_completion=True,
    rich_markup_mode="rich",
    no_args_is_help=True,
)

console = Console()
MODEL = Component


@ component_app.command()
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
        client=ctx.obj.framework.setup.DATABASE_CLIENT(),
        model=MODEL,
    )
    params = manager.get_query_params(filters)
    manager.list(params=params)


@ component_app.command()
def get(
    ctx: typer.Context,
    instance_id: str = typer.Argument(..., help="The Asset's ID"),
):
    manager = ResourceManager(
        client=ctx.obj.framework.setup.DATABASE_CLIENT(),
        model=MODEL,
    )
    try:
        manager.get(instance_id)
    except ResourceManagerException as exc:
        console.print(exc, style=error_style)


@ component_app.command()
def create(
    ctx: typer.Context,
    path: str = typer.Argument(
        ..., help="Path to JSON file with resource data"
    ),
):
    manager = ResourceManager(
        client=ctx.obj.framework.setup.DATABASE_CLIENT(),
        model=MODEL,
    )
    with open(path, "r") as fid:
        body = json.load(fid)
    manager.create(data=body)


@ component_app.command()
def upgrade(
        context: typer.Context,
        from_component_id: str = typer.Option(
            None, "--from", "-f",
            help="The ID of the component to be upgraded"),
        version: str = typer.Option(
            None, "--version", "-v",
            help="The version of the HubComponent to be upgraded to")
):
    """Upgrade a component to a new version of its HubComponent."""

    if not from_component_id or not version:
        console.print(
            "Component id and/or version cannot be empty", style=error_style)

    manager = ComponentUpgradeManager(
        context=context,
        component_id=from_component_id
    )

    new_component = manager.upgrade(version)
    console.print(
        f"New component name {new_component.name}, id {new_component.id}")
    return


@ component_app.command()
def delete(
    ctx: typer.Context,
    instance_id: str = typer.Argument(
        ..., help="The ID of the instance to be removed"
    ),
):
    manager = ResourceManager(
        client=ctx.obj.framework.setup.DATABASE_CLIENT(),
        model=MODEL,
    )
    manager.delete(instance_id)
