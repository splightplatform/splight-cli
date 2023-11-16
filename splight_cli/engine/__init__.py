import typer

from splight_cli.context import check_credentials
from splight_cli.engine.alert import alert_app
from splight_cli.engine.asset import asset_app
from splight_cli.engine.attribute import attribute_app
from splight_cli.engine.component import component_app
from splight_cli.engine.datalake import datalake_app
from splight_cli.engine.file import file_app
from splight_cli.engine.secret import secret_app

engine_app = typer.Typer(
    name="Splight Engine",
    add_completion=True,
    rich_markup_mode="rich",
    no_args_is_help=True,
)

engine_app.add_typer(alert_app, name="alert")
engine_app.add_typer(asset_app, name="asset")
engine_app.add_typer(attribute_app, name="attribute")
engine_app.add_typer(component_app, name="component")
engine_app.add_typer(datalake_app, name="datalake")
engine_app.add_typer(file_app, name="file")
engine_app.add_typer(secret_app, name="secret")


@engine_app.callback(invoke_without_command=True)
def engine_callback(ctx: typer.Context):
    check_credentials(ctx)
