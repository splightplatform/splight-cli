from typing import Optional

import typer
from cli.component import component_app
from cli.config import config_app
from cli.context import Context
from cli.engine import engine_app
from cli.hub import hub_app
from cli.version import __version__
from cli.workspace import workspace_app

app = typer.Typer(
    name="Splight Command Line",
    add_completion=True,
    rich_markup_mode="rich",
    no_args_is_help=True,
)

app.add_typer(config_app, name="configure")
app.add_typer(component_app, name="component")
app.add_typer(engine_app, name="engine")
app.add_typer(hub_app, name="hub")
app.add_typer(workspace_app, name="workspace")


def version_callback(version: bool):
    if version:
        print(__version__)
        raise typer.Exit()


@app.callback()
def main(
    ctx: typer.Context,
    version: Optional[bool] = typer.Option(
        None, "--version", "-v", callback=version_callback, is_eager=True
    ),
):
    ctx.obj = Context()
