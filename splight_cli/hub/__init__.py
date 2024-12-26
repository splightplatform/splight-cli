import typer

from splight_cli.hub.component import component_app
from splight_cli.hub.server import server_app

hub_app = typer.Typer(
    name="Splight Hub",
    add_completion=True,
    rich_markup_mode="rich",
    no_args_is_help=True,
)

hub_app.add_typer(component_app, name="component")
hub_app.add_typer(server_app, name="server")
