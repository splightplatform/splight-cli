import json

import typer
from rich.console import Console
from splight_models import File

from cli.constants import error_style
from cli.engine.manager import ResourceManager, ResourceManagerException

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


@file_app.command()
def get(
    ctx: typer.Context,
    instance_id: str = typer.Argument(..., help="The File's ID"),
    path: str = typer.Option(
        None, "--path", "-p", help="Path to save the file"
    ),
):
    manager = ResourceManager(
        client=ctx.obj.framework.setup.DATABASE_CLIENT(),
        model=MODEL,
    )
    try:
        manager.download(instance_id, path)
    except ResourceManagerException as exc:
        console.print(exc, style=error_style)


@file_app.command()
def create(
    ctx: typer.Context,
    path: str = typer.Argument(
        ..., help="Path to file to upload"
    ),
    description: str = typer.Option(
        None, "--description", "-d", help="Description of the file"
    ),
    encrypt: bool = typer.Option(
        False, "--encrypt", "-e", help="Encrypt the file"
    ),
):
    manager = ResourceManager(
        client=ctx.obj.framework.setup.DATABASE_CLIENT(),
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
        client=ctx.obj.framework.setup.DATABASE_CLIENT(),
        model=MODEL,
    )
    manager.delete(instance_id)