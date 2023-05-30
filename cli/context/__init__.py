import typer
from cli.constants import error_style
from cli.context.workspace import WorkspaceManager
from rich.console import Console

console = Console()


class Context:
    def __init__(self):
        self.__workspace = WorkspaceManager()

    @property
    def workspace(self):
        return self.__workspace

    def __repr__(self):
        return f"<Context {self.__workspace}>"


def check_credentials(ctx: typer.Context):
    settings = ctx.obj.workspace.settings

    access_id = settings.SPLIGHT_ACCESS_ID
    secret_key = settings.SPLIGHT_SECRET_KEY
    if not access_id or not secret_key:
        console.print(
            'Please set you Splight credentials with "splight configure"',
            style=error_style,
        )
        raise typer.Exit(1)
