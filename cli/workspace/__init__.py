import typer

from cli.utils.pprint import Printer

workspace_app = typer.Typer(
    name="Splight CLI Workspace",
    add_completion=True,
    rich_markup_mode="rich",
)


@workspace_app.command()
def list(ctx: typer.Context) -> None:
    try:
        results = ctx.obj.workspace.list_workspaces()
        results_colors = [
            "green" if "*" in item else Printer.DEFAULT_COLOR
            for item in results
        ]
        Printer.print_list(
            items=results, items_colors=results_colors, header="WORKSPACES"
        )
    except Exception as e:
        typer.echo(f"Error configuring Splight Hub: {str(e)}", color="red")
        return


@workspace_app.command()
def create(
    ctx: typer.Context,
    name: str = typer.Argument(..., help="The workspace's name"),
) -> None:
    try:
        ctx.obj.workspace.create_workspace(name)
        results = ctx.obj.workspace.list_workspaces()
        results_colors = [
            "green" if "*" in item else Printer.DEFAULT_COLOR
            for item in results
        ]
        Printer.print_list(
            items=results, items_colors=results_colors, header="WORKSPACES"
        )
    except Exception as e:
        typer.echo(f"Error configuring Splight Hub: {str(e)}", color="red")
        return


@workspace_app.command()
def delete(
    ctx: typer.Context,
    name: str = typer.Argument(..., help="The workspace's name"),
) -> None:
    try:
        ctx.obj.workspace.delete_workspace(name)
        typer.echo(f"Deleted workspace {name}", color="green")
    except Exception as e:
        typer.echo(e, color="red")
        return


@workspace_app.command()
def select(
    ctx: typer.Context,
    name: str = typer.Argument(..., help="The workspace's name"),
) -> None:
    try:
        ctx.obj.workspace.select_workspace(name)
        typer.echo(f"Current workspace: {name}", color="green")
    except Exception as e:
        typer.echo(f"Error configuring Splight Hub: {str(e)}", color="red")
        return
