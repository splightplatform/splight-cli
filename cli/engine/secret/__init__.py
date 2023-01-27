from typing import List, Optional

import typer
from rich.console import Console
from splight_models import Secret

from cli.constants import error_style
from cli.engine.manager import ResourceManager, ResourceManagerException

secret_app = typer.Typer(
    name="Splight Engine Secret",
    add_completion=True,
    rich_markup_mode="rich",
    no_args_is_help=True,
)

console = Console()
MODEL = Secret


@secret_app.command()
def list(
    ctx: typer.Context,
    filters: Optional[List[str]] = typer.Option(
        None,
        "--filter",
        "-f",
        help="Query param in the form key=value",
    )
):
    manager = ResourceManager(
        client=ctx.obj.framework.setup.DATABASE_CLIENT(),
        model=MODEL,
    )
    params = manager.get_query_params(filters)
    manager.list(params)


@secret_app.command()
def get(
    ctx: typer.Context,
    instance_id: str = typer.Argument(..., help="The Secret's ID"),
):
    manager = ResourceManager(
        client=ctx.obj.framework.setup.DATABASE_CLIENT(),
        model=MODEL,
    )
    try:
        manager.get(instance_id, exclude_fields=["value"])
    except ResourceManagerException as exc:
        console.print(exc, style=error_style)


@secret_app.command()
def create(
    ctx: typer.Context,
    name: str = typer.Argument(
        ..., help="Name of the secret"
    ),
    value: str = typer.Argument(
        ..., help="Value of the secret"
    ),
):
    manager = ResourceManager(
        client=ctx.obj.framework.setup.DATABASE_CLIENT(),
        model=MODEL,
    )
    manager.create({"name": name, "value": value})


@secret_app.command()
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
