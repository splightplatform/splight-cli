import sys

import typer
from splight_lib.config import (
    SplightConfigError,
    SplightConfigManager,
    Workspace,
)

config_app = typer.Typer(
    name="Splight CLI Configure",
    add_completion=True,
)


@config_app.callback(invoke_without_command=True)
def config(ctx: typer.Context):
    if ctx.invoked_subcommand:
        return

    try:
        manager = SplightConfigManager()

        typer.echo(
            typer.style(
                "Interactive configuration for Splight CLI:",
                fg="cyan",
                bold=True,
            )
        )
        current_workspace = manager.get(manager.current)
        typer.echo(
            typer.style(f"Current Workspace: {manager.current}", fg="yellow")
        )

        # Prompt for inputs
        access_id = typer.prompt(
            "SPLIGHT_ACCESS_ID",
            default=current_workspace.SPLIGHT_ACCESS_ID or "",
            show_default=True,
        )
        secret_key = typer.prompt(
            "SPLIGHT_SECRET_KEY",
            default=current_workspace.SPLIGHT_SECRET_KEY or "",
            show_default=False,
        )
        api_host = typer.prompt(
            "SPLIGHT_PLATFORM_API_HOST",
            default=current_workspace.SPLIGHT_PLATFORM_API_HOST,
            show_default=True,
        )

        # Update workspace
        updated_workspace = Workspace(
            SPLIGHT_ACCESS_ID=access_id,
            SPLIGHT_SECRET_KEY=secret_key,
            SPLIGHT_PLATFORM_API_HOST=api_host,
        )
        manager.update(manager.current, updated_workspace)

        typer.echo(
            typer.style("Configuration saved successfully.", fg="green")
        )

    except SplightConfigError as e:
        typer.echo(
            typer.style(f"Error configuring Splight CLI: {str(e)}", fg="red")
        )
        sys.exit(1)
    except Exception as e:
        typer.echo(typer.style(f"Unexpected error: {str(e)}", fg="red"))
        sys.exit(1)


@config_app.command(name="get")
def get_variable(
    ctx: typer.Context,
    var_name: str = typer.Argument(..., help="The variable name to retrieve."),
):
    try:
        manager = SplightConfigManager()
        current_workspace = manager.get(manager.current)
        variable_name = var_name.upper()

        if hasattr(current_workspace, variable_name):
            value = getattr(current_workspace, variable_name)
            typer.echo(typer.style(f"{variable_name}: {value}", fg="green"))
        else:
            typer.echo(
                typer.style(
                    f"Variable '{variable_name}' does not exist in the workspace.",
                    fg="red",
                )
            )

    except SplightConfigError as e:
        typer.echo(
            typer.style(f"Error retrieving variable: {str(e)}", fg="red")
        )
        sys.exit(1)


@config_app.command(name="set")
def set_variable(
    ctx: typer.Context,
    var_name: str = typer.Argument(..., help="The variable name to update."),
    value: str = typer.Argument(..., help="The new value for the variable."),
):
    try:
        manager = SplightConfigManager()
        current_workspace = manager.get(manager.current)
        variable_name = var_name.upper()

        if hasattr(current_workspace, variable_name):
            setattr(current_workspace, variable_name, value)
            manager.update(manager.current, current_workspace)

            typer.echo(
                typer.style(
                    f"Successfully updated '{variable_name}' to '{value}'.",
                    fg="green",
                )
            )
        else:
            typer.echo(
                typer.style(
                    f"Variable '{variable_name}' does not exist in the workspace.",
                    fg="red",
                )
            )

    except SplightConfigError as e:
        typer.echo(typer.style(f"Error updating variable: {str(e)}", fg="red"))
        sys.exit(1)
