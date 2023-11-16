import typer

from splight_cli.context import check_credentials
from splight_cli.hub.component import component_app

hub_app = typer.Typer(
    name="Splight Hub",
    add_completion=True,
    rich_markup_mode="rich",
    no_args_is_help=True,
)

hub_app.add_typer(component_app, name="component")


@hub_app.callback(invoke_without_command=True)
def hub_callback(ctx: typer.Context):
    check_credentials(ctx)
