import logging

import typer
from rich.console import Console

from cli.constants import error_style
from cli.context import check_credentials
from cli.solution.solution import SolutionManager

solution_app = typer.Typer(
    name="Splight Solution",
    add_completion=True,
    rich_markup_mode="rich",
    no_args_is_help=True,
)

logger = logging.getLogger()
console = Console()


@solution_app.callback(invoke_without_command=True)
def callback(ctx: typer.Context):
    check_credentials(ctx)


@solution_app.command()
def plan(
    ctx: typer.Context,
    plan_file: str = typer.Argument(..., help="Path to plan yaml file."),
    state_file: str = typer.Option(
        None, "--state", "-s", help="Path to state yaml file."
    ),
) -> None:
    try:
        manager = SolutionManager(plan_file, state_file, apply=False)
        manager.execute()
    except Exception as e:
        console.print(f"Error planning solution: {str(e)}", style=error_style)
        raise typer.Exit(code=1)


@solution_app.command()
def apply(
    ctx: typer.Context,
    plan_file: str = typer.Argument(..., help="Path to plan yaml file."),
    state_file: str = typer.Option(
        None, "--state", "-s", help="Path to state yaml file."
    ),
) -> None:
    try:
        manager = SolutionManager(plan_file, state_file, apply=True)
        manager.execute()
    except Exception as e:
        console.print(f"Error applying solution: {str(e)}", style=error_style)
        raise typer.Exit(code=1)
