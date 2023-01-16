import typer
from rich.console import Console
from rich.table import Table
from splight_models import Asset
from tabulate import tabulate

from cli.engine.endpoint import APIEndpoint

asset_app = typer.Typer(
    name="Splight Engine Asset",
    add_completion=True,
    rich_markup_mode="rich",
    no_args_is_help=True,
)

console = Console()
PATH = "asset/"


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
    endpoint = APIEndpoint(
        client=ctx.obj.framework.setup.DATABASE_CLIENT(),
        model=Asset,
    )
    instances = endpoint.list(skip=skip, limit=limit)
    table = Table("", "ID", "Name")
    _ = [
        table.add_row(str(counter), item.id, item.name)
        for counter, item in enumerate(instances)
    ]
    console.print(table)


@asset_app.command()
def get(
    ctx: typer.Context,
    instance_id: str = typer.Argument(..., help="The Asset's ID"),
):
    endpoint = APIEndpoint(
        client=ctx.obj.framework.setup.DATABASE_CLIENT(),
        model=Asset,
    )
    instance = endpoint.get(instance_id)
    table = Table(title=f"Asset = {instance.name}", show_header=False)
    _ = [
        table.add_row(key, str(value))
        for key, value in instance.dict().items()
    ]
    console.print(table)


@asset_app.command()
def create():
    print("create")


@asset_app.command()
def delete():
    print("delete")


@asset_app.command()
def update():
    print("update")
