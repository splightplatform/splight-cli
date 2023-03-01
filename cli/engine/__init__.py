import typer

from cli.context import check_credentials
from cli.engine.alert import alert_app
from cli.engine.asset import asset_app
from cli.engine.attribute import attribute_app
from cli.engine.component import component_app
from cli.engine.graph import graph_app
from cli.engine.query import query_app
from cli.engine.file import file_app
from cli.engine.secret import secret_app
from cli.engine.setpoint import setpoint_app
from cli.engine.datalake import datalake_app

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
engine_app.add_typer(graph_app, name="graph")
engine_app.add_typer(query_app, name="query")
engine_app.add_typer(file_app, name="file")
engine_app.add_typer(secret_app, name="secret")
engine_app.add_typer(setpoint_app, name="setpoint")
engine_app.add_typer(datalake_app, name="datalake")


@engine_app.callback(invoke_without_command=True)
def engine_callback(ctx: typer.Context):
    check_credentials(ctx)
