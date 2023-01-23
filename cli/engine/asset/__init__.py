import json

import typer
from rich.console import Console
from rich.table import Table
from splight_models import Asset

from cli.constants import error_style
# from cli.engine.endpoint import APIEndpoint
from cli.engine.manager import ResourceManager, ResourceManagerException

asset_app = typer.Typer(
    name="Splight Engine Asset",
    add_completion=True,
    rich_markup_mode="rich",
    no_args_is_help=True,
)

console = Console()
MODEL = Asset


@asset_app.command()
def list(
    ctx: typer.Context,
    skip: int = typer.Option(
        0, "--skip", "-s", help="Number of element to skip"
    ),
    limit: int = typer.Option(
        -1, "--limit", "-l", help="Limit the number of listed elements"
    ),
):
    manager = ResourceManager(
        client=ctx.obj.framework.setup.DATABASE_CLIENT(),
        model=MODEL,
    )
    manager.list(skip=skip, limit=limit)


@asset_app.command()
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


@asset_app.command()
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


@asset_app.command()
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
