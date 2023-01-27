# import click
import typer

# from functools import wraps
from rich.console import Console

from cli.constants import error_style
from cli.context.framework import FrameworkManager
from cli.context.workspace import WorkspaceManager

console = Console()


class Context:
    def __init__(self):
        self.__workspace = WorkspaceManager()
        self.__framework = FrameworkManager()

    @property
    def framework(self):
        self.__framework.configure(self.workspace.settings.dict())
        return self.__framework

    @property
    def workspace(self):
        return self.__workspace

    def __repr__(self):
        return f"<Context {self.__workspace}>"


# pass_context = click.make_pass_decorator(Context)


def check_credentials(ctx: typer.Context):
    settings = ctx.obj.workspace.settings

    access_id = settings.SPLIGHT_ACCESS_ID
    secret_key = settings.SPLIGHT_SECRET_KEY
    if access_id is None or secret_key is None:
        console.print(
            'Please set you Splight credentials with "splight configure"',
            style=error_style,
        )
        raise typer.Exit(1)


# def needs_credentials(f):
#     @wraps(f)
#     def wrapper(ctx: typer.Context, *args, **kwargs):
#         __import__('ipdb').set_trace()
#         access_id = ctx.workspace.settings.SPLIGHT_ACCESS_ID
#         secret_key = ctx.workspace.settings.SPLIGHT_SECRET_KEY
#         if access_id is None or secret_key is None:
#             click.secho(
#                 "Please set your Splight credentials. Use \"splightcli configure\"",
#                 fg="red"
#             )
#             exit(1)
#         return f(ctx, *args, **kwargs)
#     return wrapper
