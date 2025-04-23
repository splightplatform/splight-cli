from typing import Optional

import typer
from rich.console import Console
from splight_lib.settings import workspace_settings

from splight_cli.component import component_app
from splight_cli.config import config_app
from splight_cli.engine import engine_app
from splight_cli.version import __version__
from splight_cli.workspace import workspace_app

console = Console()

app = typer.Typer(
    name="Splight Command Line",
    add_completion=True,
    rich_markup_mode="rich",
    pretty_exceptions_enable=False,
)


app.add_typer(config_app, name="configure")
app.add_typer(component_app, name="component")
app.add_typer(engine_app, name="engine")
app.add_typer(workspace_app, name="workspace")


def ensure_settings(ctx: typer.Context):
    if not workspace_settings.configured:
        console.print(
            "Please run `splight configure` or set the corresponding environment variables.",
            style="red",
        )
        raise typer.Exit(code=1)


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: Optional[bool] = typer.Option(
        None, "--version", "-v", is_eager=True
    ),
) -> None:
    if version:
        console.print(__version__)
        raise typer.Exit()

    command = ctx.invoked_subcommand

    if command and command not in [
        "workspace",
        "configure",
    ]:
        # Forward the check to every sub command
        ensure_settings(ctx)

    if command is None:
        ctx.get_help()
