from typing import List

import typer
from rich.console import Console
from cli.constants import error_style
from cli.engine.manager import DatalakeManager, DatalakeManagerException

datalake_app = typer.Typer(
    name="Splight Engine Datalake",
    add_completion=True,
    rich_markup_mode="rich",
    no_args_is_help=True,
)
console = Console()


def _parse_filter_option(values):
    result = {}
    for value in values:
        k, v = value.split('=')
        result[k] = v
    return result


@datalake_app.command()
def list(
    ctx: typer.Context,
    skip: int = typer.Option(
        0, "--skip", "-s", help="Number of element to skip"
    ),
    limit: int = typer.Option(
        -1, "--limit", "-l", help="Limit the number of listed elements"
    ),
):
    manager = DatalakeManager(
        db_client=ctx.obj.framework.setup.DATABASE_CLIENT(),
        dl_client=ctx.obj.framework.setup.DATALAKE_CLIENT(),
    )
    manager.list(skip, limit)


@datalake_app.command()
def dump(
    ctx: typer.Context,
    collection: str = typer.Argument(
        ..., help="Collection name to dump"
    ),
    path: str = typer.Option(
        './dump.csv', "--path", "-p", help="Path name to dump"
    ),
    filter: List[str] = typer.Option(
        None, "--filter", "-f", help="Filter to apply"
    ),
):
    filters = _parse_filter_option(filter)
    manager = DatalakeManager(
        db_client=ctx.obj.framework.setup.DATABASE_CLIENT(),
        dl_client=ctx.obj.framework.setup.DATALAKE_CLIENT(),
    )
    try:
        manager.dump(
            collection=collection,
            path=path,
            filters=filters
        )
    except DatalakeManagerException as exc:
        console.print(exc, style=error_style)


@datalake_app.command()
def load(
    ctx: typer.Context,
    collection: str = typer.Argument(..., help="Collection name to load"),
    path: str = typer.Option(
        ..., "--path", "-p", help="Path to file to load"
    ),
):
    manager = DatalakeManager(
        db_client=ctx.obj.framework.setup.DATABASE_CLIENT(),
        dl_client=ctx.obj.framework.setup.DATALAKE_CLIENT(),
    )
    try:
        manager.load(
            collection=collection,
            path=path
        )
    except DatalakeManagerException as exc:
        console.print(exc, style=error_style)
