import typer
from rich.console import Console

from splight_cli.context import check_credentials
from splight_cli.solution.parser import Parser
from splight_cli.solution.resource import ResourceManager
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


# FIXME: find a nice way to print the exceptions.
# Take into account that most exception messages are short and do not have
# that much content. I would include the traceback, or at least some part of it.
# Another option is to not catch them, and show the entire error, so the user can
# debug it.
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
    specs, dependency_graph = parser.parse()

    manager = ResourceManager(
        state=state,
        specs=specs,
        dependency_graph=dependency_graph,
    )
    manager.refresh()
    plan = manager.plan()
    if plan:
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
    specs, dependency_graph = parser.parse()

    manager = ResourceManager(
        state=state,
        specs=specs,
        dependency_graph=dependency_graph,
    )
    manager.refresh()
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

    manager = ResourceManager(state=state)
    manager.refresh()
