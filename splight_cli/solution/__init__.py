import typer
from rich.console import Console

from splight_cli.constants import error_style
from splight_cli.context import check_credentials
from splight_cli.solution.parser import Parser
from splight_cli.solution.resources import ResourceManager
from splight_cli.solution.state import State

solution_app = typer.Typer(
    name="Splight Solution",
    add_completion=True,
    rich_markup_mode="rich",
    no_args_is_help=True,
)

console = Console()


@solution_app.callback(invoke_without_command=True)
def callback(ctx: typer.Context):
    check_credentials(ctx)


@solution_app.command()
def apply(
    ctx: typer.Context,
    spec_file: str = typer.Argument(..., help="Path to the spec file."),
    state_file: str = typer.Option(
        "state.json", "--state", "-s", help="Path to the state file."
    ),
) -> None:
    try:
        state = State(path=state_file)
        parser = Parser(spec_file=spec_file)
        manager = ResourceManager()

        state.load()

        spec_resources = parser.parse()

        manager.sync(state)
        manager.create(spec_resources, state)
        manager.delete(spec_resources, state)

    except Exception as e:
        console.print(f"Error applying solution: {str(e)}", style=error_style)
        raise typer.Exit(code=1)
