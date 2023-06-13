import logging
from pathlib import Path
from typing import Optional

import typer
from cli.component.component import ComponentManager
from cli.constants import error_style, success_style
from cli.context import check_credentials
from rich.console import Console

component_app = typer.Typer(
    name="Splight Component",
    add_completion=True,
    rich_markup_mode="rich",
    no_args_is_help=True,
)

logger = logging.getLogger()
console = Console()


@component_app.callback(invoke_without_command=True)
def callback(ctx: typer.Context):
    check_credentials(ctx)


@component_app.command()
def create(
    ctx: typer.Context,
    name: str = typer.Argument(..., help="Component's name"),
    version: str = typer.Option(
        "0.1.0", "--version", "-v", help="Component's version"
    ),
    path: str = typer.Option(".", "--path", "-p", help="Component's path"),
) -> None:
    try:
        manager = ComponentManager()
        manager.create(name, version, path)
        abs_path = str(Path(path).resolve())
        console.print(
            f"Component {name} created successfully in {abs_path}",
            style=success_style,
        )
    except Exception as e:
        console.print(f"Error creating component: {str(e)}", style=error_style)
        typer.Exit(1)


@component_app.command()
def run(
    ctx: typer.Context,
    path: str = typer.Argument(..., help="Path to component source code"),
    component_id: str = typer.Option(
        None, "--component-id", "-id", help="Component's ID"
    ),
    local_dev: bool = typer.Option(False, "--local"),
    input: Optional[str] = typer.Option(
        None, "--input", "-i", help="Input Values [Deprecated]"
    ),
) -> None:
    try:
        manager = ComponentManager()
        console.print("Running component...", style=success_style)
        manager.run(
            path, component_id=component_id, local_environment=local_dev
        )
    except Exception as e:
        logger.exception(e)
        console.print(f"Error running component: {str(e)}", style=error_style)
        typer.Exit(1)


@component_app.command()
def install_requirements(
    ctx: typer.Context,
    path: str = typer.Argument(..., help="Path to component source code"),
) -> None:
    try:
        manager = ComponentManager()
        console.print(
            "Installing component requirements...", style=success_style
        )
        manager.install_requirements(path)
    except Exception as e:
        console.print(
            f"Error installing component requirements: {str(e)}",
            style=error_style,
        )
        typer.Exit(1)


@component_app.command()
def readme(
    ctx: typer.Context,
    path: str = typer.Argument(..., help="Path to component source code"),
    force: Optional[bool] = typer.Option(
        False,
        "--force",
        "-f",
        help="Delete if a Readme exists",
    ),
) -> None:
    try:
        manager = ComponentManager()
        console.print("Generating component README...", style=success_style)
        manager.readme(path, force)
    except Exception as e:
        console.print(
            f"Error generating component README: {str(e)}", style=error_style
        )
        typer.Exit(1)


@component_app.command()
def test(
    ctx: typer.Context,
    path: str = typer.Argument(..., help="Path to component test code"),
    name: Optional[str] = typer.Option(
        None,
        "--name",
        "-n",
        help="Name of the only test that you want to run",
    ),
    debug: Optional[bool] = typer.Option(
        False, "--debug", "-d", help="To enable debug mode using pdb"
    ),
) -> None:
    try:
        manager = ComponentManager()
        console.print("Testing component...", style=success_style)
        manager.test(path=path, name=name, debug=debug)
    except Exception as e:
        logger.exception(e)
        console.print(f"Error testing component: {str(e)}", style=error_style)
        typer.Exit(1)
