import json
import logging
from typing import List, Optional

import typer
from rich.console import Console

from cli.context import check_credentials
from cli.component.component import Component
from cli.constants import error_style, success_style

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
    version: str = typer.Argument(..., help="Component's version"),
) -> None:
    try:
        component = Component(ctx.obj)
        component.create(name, version)
        console.print(
            f"Component {name} created successfully", style=success_style
        )

    except Exception as e:
        console.print(
            f"Error creating component: {str(e)}", style=success_style
        )
        typer.Exit(1)


@component_app.command()
def run(
    ctx: typer.Context,
    path: str = typer.Argument(..., help="Path to component source code"),
    input: str = typer.Option(None, "--input", "-i", help="Input Values"),
    component_id: str = typer.Option(
        None, "--component-id", "-id", help="Component's ID"
    ),
) -> None:
    try:
        component = Component(ctx.obj)
        console.print("Running component...", style=success_style)
        input = json.loads(input) if input else None
        component.run(path, input_parameters=input, component_id=component_id)
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
        component = Component(ctx.obj)
        console.print(
            "Installing component requirements...", style=success_style
        )
        component.install_requirements(path)
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
    )
) -> None:
    try:
        component = Component(ctx.obj)
        console.print("Generating component README...", style=success_style)
        component.readme(path, force)
    except Exception as e:
        console.print(
            f"Error generating component README: {str(e)}",
            style=error_style
        )
        typer.Exit(1)



