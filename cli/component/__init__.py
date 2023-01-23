import json
import logging
import os
import shutil
import sys

import typer
from rich.console import Console
from rich.table import Table

from cli.component.component import Component, ComponentAlreadyExistsException
from cli.constants import error_style, success_style

component_app = typer.Typer(
    name="Splight Component",
    add_completion=True,
    rich_markup_mode="rich",
    no_args_is_help=True,
)

logger = logging.getLogger()
console = Console()


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
def push(
    ctx: typer.Context,
    path: str = typer.Argument(..., help="Path to component source code"),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Overwrite existing component in Splight HUB",
    ),
    public: bool = typer.Option(
        False, "--public", "-p", help="Make the component public"
    ),
) -> None:
    try:
        component = Component(ctx.obj)
        try:
            component.push(path, force)
            console.print(
                "Component pushed successfully to Splight Hub",
                style=success_style,
            )
        except ComponentAlreadyExistsException:
            value = typer.prompt(
                typer.style(
                    "This component already exists in Splight Hub (you can use -f to force pushing). Do you want to overwrite it? (y/n)",
                    fg="yellow",
                ),
                type=str,
            )
            if value in ["y", "Y"]:
                component.push(force=True, public=public)
                typer.echo(
                    "Component pushed successfully to Splight Hub",
                    color="green",
                )
            else:
                typer.echo("Component not pushed", color="blue")
    except Exception as e:
        console.print(f"Error pushing component: {str(e)}", style=error_style)
        typer.Exit(1)


@component_app.command()
def pull(
    ctx: typer.Context,
    name: str = typer.Argument(..., help="The component's name"),
    version: str = typer.Argument(..., help="The component's version"),
) -> None:
    path = os.path.abspath(".")
    component = Component(ctx.obj)
    try:
        component.pull(name, version)
        console.print(
            f"Component {name}-{version} pulled successfully in {path}",
            style=success_style,
        )
    except Exception as e:
        component_path = os.path.join(path, f"{name}/{version}/")
        if os.path.exists(component_path):
            shutil.rmtree(component_path)
        console.print(f"Error pulling component: {str(e)}", style=error_style)
        typer.Exit(1)


@component_app.command()
def delete(
    ctx: typer.Context,
    name: str = typer.Argument(..., help="The component's name"),
    version: str = typer.Argument(..., help="The component's version"),
) -> None:
    try:
        response = typer.prompt(
            typer.style(
                f"Are you sure you want to delete {name}-{version}? This operation will delete the component from Splight Hub and it won't be recoverable. (y/n)",
                fg="yellow",
            ),
            type=str,
            default="n",
            show_default=False,
        )
        if response not in ["y", "Y"]:
            typer.echo("Component not deleted", color="blue")
            sys.exit(1)
        # path = os.path.abspath(".")
        component = Component(ctx.obj)
        component.delete(name, version)
        console.print(
            f"Component {name}-{version} deleted successfully",
            style=success_style,
        )
    except Exception as e:
        logger.exception(e)
        console.print(f"Error deleting component: {str(e)}", style=error_style)
        typer.Exit(1)


@component_app.command()
def list(ctx: typer.Context) -> None:
    try:
        results = Component(ctx.obj).list()
        table = Table("Name")
        for item in results:
            table.add_row(item["name"])
        console.print(table)
    except Exception as e:
        console.print(f"Error listing component: {str(e)}", style=error_style)
        typer.Exit(1)


@component_app.command()
def versions(
    ctx: typer.Context,
    name: str = typer.Argument(..., help="Component's name"),
) -> None:
    try:
        results = Component(ctx.obj).versions(name)
        table = Table("Name", "Version", "Verification", "Privacy Policy")
        for item in results:
            table.add_row(
                item["name"],
                item["version"],
                item["verification"],
                item["privacy_policy"],
            )
        console.print(table)
    except Exception as e:
        console.print(f"Error listing component: {str(e)}", style=error_style)
        logger.exception(e)
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
