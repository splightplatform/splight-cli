import typer
from splight_models import Asset
from tabulate import tabulate

from cli.engine.endpoint import APIEndpoint
from cli.utils.headers import extract_headers

asset_app = typer.Typer(
    name="Splight Engine Asset",
    add_completion=True,
    rich_markup_mode="rich",
)

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
    instances = endpoint.list(limit=limit)
    table = tabulate(
        [[item.id, item.name] for item in instances],
        headers=["id", "name"],
        showindex=True,
        stralign="left",
    )
    print(table)


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
    print(tabulate([[key, value] for key, value in instance.dict().items()]))


@asset_app.command()
def create():
    print("create")


@asset_app.command()
def delete():
    print("delete")


@asset_app.command()
def update():
    print("update")
