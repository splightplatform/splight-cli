import click
from enum import Enum
from cli.context.workspace import WorkspaceManager
from cli.context.framework import FrameworkManager


class PrivacyPolicy(str, Enum):
    PUBLIC = "public"
    PRIVATE = "private"

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


pass_context = click.make_pass_decorator(Context)

from functools import wraps
def needs_credentials(f):
    @wraps(f)
    def wrapper(ctx, *args, **kwargs):
        if ctx.workspace.settings.SPLIGHT_ACCESS_ID is None or ctx.workspace.settings.SPLIGHT_SECRET_KEY is None:
            click.secho(f"Please set your Splight credentials. Use \"splightcli configure\"", fg='red')
            exit(1)
        return f(ctx, *args, **kwargs)
    return wrapper
