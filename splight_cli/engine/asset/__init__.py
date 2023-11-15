import json
from typing import List, Optional

import typer
from rich.console import Console
from splight_lib.models import Asset

from splight_cli.constants import error_style
from splight_cli.engine.manager import (
    ResourceManager,
    ResourceManagerException,
)

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
    manager.list(params)


@asset_app.command()
def get(
    ctx: typer.Context,
    instance_id: str = typer.Argument(..., help="The Asset's ID"),
):
    manager = ResourceManager(
        model=MODEL,
    )
    try:
        manager.get(instance_id)
    except Exception as exc:
        console.print(exc, style=error_style)


@asset_app.command()
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


@asset_app.command()
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


@asset_app.command()
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
