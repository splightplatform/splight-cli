from typing import Optional

import typer
from rich.console import Console

from splight_cli.component import component_app
from splight_cli.config import config_app
from splight_cli.constants import error_style
from splight_cli.context import Context
from splight_cli.context.exceptions import MissingConfigurationFile
from splight_cli.engine import engine_app
from splight_cli.hub import hub_app
from splight_cli.solution import solution_app
from splight_cli.version import __version__
from splight_cli.workspace import workspace_app

console = Console()
app = typer.Typer(
    name="Splight Command Line",
    add_completion=True,
    rich_markup_mode="rich",
    invoke_without_command=True,
    pretty_exceptions_enable=False,
)

app.add_typer(config_app, name="configure")
app.add_typer(component_app, name="component")
app.add_typer(engine_app, name="engine")
app.add_typer(hub_app, name="hub")
app.add_typer(solution_app, name="solution")
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
) -> None:
    try:
        ctx.obj = Context(
            new_workspace=(
                True if ctx.invoked_subcommand == "configure" else False
            )
        )
    except MissingConfigurationFile as exc:
        console.print(
            (
                f"Error running Splight: {str(exc)}. "
                "Run command 'splight configure' to configure your environment"
            ),
            style=error_style,
        )
        raise typer.Exit(code=1)
    if ctx.invoked_subcommand is None:
        ctx.get_help()
