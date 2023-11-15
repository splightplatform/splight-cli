from typing import List

import typer
from rich.console import Console
from splight_lib.models import Boolean, Number, String

from splight_cli.constants import error_style
from splight_cli.engine.manager import (
    DatalakeManager,
    DatalakeManagerException,
)

datalake_app = typer.Typer(
    name="Splight Engine Datalake",
    add_completion=True,
    rich_markup_mode="rich",
    no_args_is_help=True,
)
console = Console()

MODEL_MAP = {
    "Number": Number,
    "String": String,
    "Boolean": Boolean,
}


def _parse_filter_option(values):
    result = {}
    for value in values:
        k, v = value.split("=")
        result[k] = v
    return result


@datalake_app.command()
def dump(
    ctx: typer.Context,
    type: str = typer.Argument(
        ..., help="Data type to dump eg. Number, String, Boolean"
    ),
    asset: str = typer.Argument(..., help="Asset id to dump"),
    attribute: str = typer.Argument(..., help="Attribute id to dump"),
    path: str = typer.Option(
        "./dump.csv", "--path", "-p", help="Path name to dump"
    ),
    filter: List[str] = typer.Option(
        None, "--filter", "-f", help="Filter to apply"
    ),
):
    if type not in MODEL_MAP:
        raise typer.BadParameter(f"Type {type} not supported")

    filters = _parse_filter_option(filter)
    filters.update({"asset": asset, "attribute": attribute})
    manager = DatalakeManager(
        model=MODEL_MAP[type],
    )
    try:
        manager.dump(path=path, filters=filters)
    except DatalakeManagerException as exc:
        console.print(exc, style=error_style)


@datalake_app.command()
def load(
    ctx: typer.Context,
    type: str = typer.Argument(
        ..., help="Data type to dump eg. Number, String, Boolean"
    ),
    path: str = typer.Option(..., "--path", "-p", help="Path to file to load"),
):
    if type not in MODEL_MAP:
        raise typer.BadParameter(f"Type {type} not supported")

    manager = DatalakeManager(
        model=MODEL_MAP[type],
    )

    try:
        manager.load(path=path)
    except DatalakeManagerException as exc:
        console.print(exc, style=error_style)
