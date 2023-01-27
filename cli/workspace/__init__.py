import typer
from rich.console import Console
from rich.table import Table

from cli.constants import error_style, success_style

workspace_app = typer.Typer(
    name="Splight CLI Workspace",
    add_completion=True,
    rich_markup_mode="rich",
)
console = Console()


@workspace_app.command()
def list(ctx: typer.Context) -> None:
    try:
        results = ctx.obj.workspace.list_workspaces()
        table = Table("WORKSPACES", show_lines=False, show_edge=False)
        _ = [
            table.add_row(item, style=success_style if "*" in item else None)
            for item in results
        ]
        console.print(table)
    except Exception as e:
        console.print(
            f"Error configuring Splight Hub: {str(e)}", style=error_style
        )
        typer.Exit(1)


@workspace_app.command()
def create(
    ctx: typer.Context,
    name: str = typer.Argument(..., help="The workspace's name"),
) -> None:
    try:
        ctx.obj.workspace.create_workspace(name)
        results = ctx.obj.workspace.list_workspaces()
        table = Table("WORKSPACES", show_lines=False, show_edge=False)
        _ = [
            table.add_row(item, style=success_style if "*" in item else None)
            for item in results
        ]
        console.print(table)
    except Exception as e:
        console.print(
            f"Error configuring Splight Hub: {str(e)}", style=error_style
        )
        typer.Exit(1)


@workspace_app.command()
def delete(
    ctx: typer.Context,
    name: str = typer.Argument(..., help="The workspace's name"),
) -> None:
    try:
        ctx.obj.workspace.delete_workspace(name)
        console.print(f"Deleted workspace {name}", style=success_style)
    except Exception as e:
        console.print(e, style=error_style)
        typer.Exit(1)


@workspace_app.command()
def select(
    ctx: typer.Context,
    name: str = typer.Argument(..., help="The workspace's name"),
) -> None:
    try:
        ctx.obj.workspace.select_workspace(name)
        console.print(f"Current workspace: {name}", style=success_style)
    except Exception as e:
        console.print(
            f"Error configuring Splight Hub: {str(e)}", style=error_style
        )
        typer.Exit(1)
