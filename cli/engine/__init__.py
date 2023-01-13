import typer

from cli.engine.asset import asset_app


engine_app = typer.Typer(
    name="Splight Engine",
    add_completion=True,
    rich_markup_mode="rich",
)

engine_app.add_typer(asset_app, name="asset")


@engine_app.callback(invoke_without_command=True)
def engine_callback(ctx: typer.Context):
    pass
