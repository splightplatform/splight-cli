import typer
from rich.console import Console
from splight_lib.models import Component

from splight_cli.constants import error_style
from splight_cli.hub.solution.solution_manager import HubSolutionManager

solution_app = typer.Typer(
    name="Splight Hub Solution",
    add_completion=True,
    rich_markup_mode="rich",
    no_args_is_help=True,
)

console = Console()
MODEL = Component


@solution_app.command()
def push(
    ctx: typer.Context,
    path: str = typer.Argument(..., help="Path to solution files"),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Overwrite existing solution in Splight HUB",
    ),
):
    try:
        manager = HubSolutionManager()
        manager.push(path, force=force)
    except Exception as exc:
        console.print(f"Error pushing solution: {exc}", style=error_style)
        raise typer.Exit(code=1)


# TODO: Define the pull command
@solution_app.command()
def pull(
    ctx: typer.Context,
    name: str = typer.Argument(..., help="The component's name"),
    version: str = typer.Argument(..., help="The component's version"),
):
    try:
        manager = HubSolutionManager()
        manager.pull(name=name, version=version)
    except Exception as exc:
        console.print(f"Error pulling solution: {exc}", style=error_style)
        raise typer.Exit(code=1)


@solution_app.command()
def list(ctx: typer.Context):
    try:
        manager = HubSolutionManager()
        manager.list_solutions()
    except Exception as exc:
        console.print(f"Error listing components: {exc}", style=error_style)
        raise typer.Exit(code=1)
