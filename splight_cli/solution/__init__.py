import typer
from rich.console import Console

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
    _: typer.Context,
    spec_file: str = typer.Argument(..., help="Path to the spec file."),
    state_file: str = typer.Option(
        "state.json", "--state", "-s", help="Path to the state file."
    ),
) -> None:
    state = State(path=state_file)
    state.load()

    parser = Parser(spec_file=spec_file)
    spec_resources = parser.parse()

    manager = ResourceManager(
        spec_resources=spec_resources,
        state=state,
    )
    manager.sync()
    manager.plan()
    manager.apply()


@solution_app.command()
def plan(
    _: typer.Context,
    spec_file: str = typer.Argument(..., help="Path to the spec file."),
    state_file: str = typer.Option(
        "state.json", "--state", "-s", help="Path to the state file."
    ),
) -> None:
    state = State(path=state_file)
    state.load()

    parser = Parser(spec_file=spec_file)
    spec_resources = parser.parse()

    manager = ResourceManager(
        spec_resources=spec_resources,
        state=state,
    )
    manager.sync()
    manager.plan()


@solution_app.command()
def refresh(
    _: typer.Context,
    state_file: str = typer.Option(
        "state.json", "--state", "-s", help="Path to the state file."
    ),
) -> None:
    state = State(path=state_file)
    state.load()

    manager = ResourceManager(
        spec_resources=[],
        state=state,
    )
    manager.sync(save=True)
