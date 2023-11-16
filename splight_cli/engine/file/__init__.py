from typing import List, Optional

import typer
from rich.console import Console
from splight_lib.models import File

from splight_cli.constants import error_style
from splight_cli.engine.manager import (
    ResourceManager,
    ResourceManagerException,
)

file_app = typer.Typer(
    name="Splight Engine File",
    add_completion=True,
    rich_markup_mode="rich",
    no_args_is_help=True,
)

console = Console()
MODEL = File


@file_app.command()
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


@file_app.command()
def get(
    ctx: typer.Context,
    instance_id: str = typer.Argument(..., help="The File's ID"),
    path: str = typer.Option(
        None, "--path", "-p", help="Path to save the file"
    ),
):
    manager = ResourceManager(
        model=MODEL,
    )
    try:
        manager.download(instance_id, path)
    except ResourceManagerException as exc:
        console.print(exc, style=error_style)


@file_app.command()
def create(
    ctx: typer.Context,
    path: str = typer.Argument(..., help="Path to file to upload"),
    description: str = typer.Option(
        None, "--description", "-d", help="Description of the file"
    ),
    encrypt: bool = typer.Option(
        False, "--encrypt", "-e", help="Encrypt the file"
    ),
):
    manager = ResourceManager(
        model=MODEL,
    )
    file = MODEL(
        description=description,
        encrypted=encrypt,
        file=path,
    )
    manager.create(file)


@file_app.command()
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


@file_app.command()
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
