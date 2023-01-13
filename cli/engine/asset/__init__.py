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
def list(ctx: typer.Context):
    endpoint = APIEndpoint(
        url=ctx.obj.workspace.settings.SPLIGHT_PLATFORM_API_HOST,
        path=PATH,
        model=Asset,
        headers=extract_headers(ctx.obj.workspace.settings),
    )
    instances = endpoint.list()
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
        url=ctx.obj.workspace.settings.SPLIGHT_PLATFORM_API_HOST,
        path=PATH,
        model=Asset,
        headers=extract_headers(ctx.obj.workspace.settings),
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
