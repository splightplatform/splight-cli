import typer

from cli.context import check_credentials
from cli.engine.asset import asset_app
from cli.engine.attribute import attribute_app
from cli.engine.component import component_app
from cli.engine.graph import graph_app
from cli.engine.query import query_app

engine_app = typer.Typer(
    name="Splight Engine",
    add_completion=True,
    rich_markup_mode="rich",
    no_args_is_help=True,
)

engine_app.add_typer(asset_app, name="asset")
engine_app.add_typer(attribute_app, name="attribute")
engine_app.add_typer(component_app, name="component")
engine_app.add_typer(graph_app, name="graph")
engine_app.add_typer(query_app, name="query")


@engine_app.callback(invoke_without_command=True)
def engine_callback(ctx: typer.Context):
    check_credentials(ctx)
