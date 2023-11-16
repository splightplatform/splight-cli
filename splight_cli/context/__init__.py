import typer
from rich.console import Console

from splight_cli.constants import error_style
from splight_cli.context.workspace import WorkspaceManager

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
        raise typer.Exit(code=1)
