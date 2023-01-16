import typer

from cli.engine.asset import asset_app


engine_app = typer.Typer(
    name="Splight Engine",
    add_completion=True,
    rich_markup_mode="rich",
    no_args_is_help=True,
)

engine_app.add_typer(asset_app, name="asset")
