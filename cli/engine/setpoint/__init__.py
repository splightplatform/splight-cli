import json
from typing import List, Optional

import typer
from rich.console import Console
from splight_lib.models import SetPoint

from cli.constants import error_style
from cli.engine.manager import ResourceManager, ResourceManagerException

setpoint_app = typer.Typer(
    name="Splight Engine SetPoint",
    add_completion=True,
    rich_markup_mode="rich",
    no_args_is_help=True,
)

console = Console()
MODEL = SetPoint


@setpoint_app.command()
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


@setpoint_app.command()
def get(
    ctx: typer.Context,
    instance_id: str = typer.Argument(..., help="The setpoit's ID"),
):
    manager = ResourceManager(
        model=MODEL,
    )
    try:
        manager.get(instance_id)
    except ResourceManagerException as exc:
        console.print(exc, style=error_style)


@setpoint_app.command()
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


@setpoint_app.command()
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
