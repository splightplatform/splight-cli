import logging
from uuid import UUID

import typer
from rich.console import Console

from cli.constants import error_style
from cli.context import check_credentials
from cli.solution.models import ElementType
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
    yes_to_all: bool = typer.Option(False, "--yes", "-y"),
) -> None:
    try:
        manager = SolutionManager(plan_file, state_file, yes_to_all=yes_to_all)
        manager.plan()
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
    yes_to_all: bool = typer.Option(False, "--yes", "-y"),
) -> None:
    try:
        manager = SolutionManager(plan_file, state_file, yes_to_all=yes_to_all)
        manager.apply()
    except Exception as e:
        console.print(f"Error applying solution: {str(e)}", style=error_style)
        raise typer.Exit(code=1)


@solution_app.command("import")
def _import(
    ctx: typer.Context,
    element: ElementType = typer.Argument(
        ...,
        case_sensitive=False,
        help="Either 'asset' or 'component'.",
    ),
    id: UUID = typer.Argument(
        ..., help="The asset or component uuid to be fetched."
    ),
    plan_file: str = typer.Argument(..., help="Path to plan yaml file."),
    state_file: str = typer.Option(
        None, "--state", "-s", help="Path to state yaml file."
    ),
    yes_to_all: bool = typer.Option(False, "--yes", "-y"),
) -> None:
    try:
        manager = SolutionManager(plan_file, state_file, yes_to_all=yes_to_all)
        manager.import_element(element, id)
    except Exception as e:
        console.print(
            f"Error importing {element}: {str(e)}", style=error_style
        )
        raise typer.Exit(code=1)


@solution_app.command()
def destroy(
    ctx: typer.Context,
    plan_file: str = typer.Argument(..., help="Path to plan yaml file."),
    state_file: str = typer.Option(
        None, "--state", "-s", help="Path to state yaml file."
    ),
    yes_to_all: bool = typer.Option(False, "--yes", "-y"),
) -> None:
    try:
        manager = SolutionManager(plan_file, state_file, yes_to_all=yes_to_all)
        manager.destroy()
    except Exception as e:
        console.print(
            f"Error destroying solution: {str(e)}", style=error_style
        )
        raise typer.Exit(code=1)
