import click
from functools import wraps
from cli.context.workspace import WorkspaceManager
from cli.context.framework import FrameworkManager

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


def needs_credentials(f):
    @wraps(f)
    def wrapper(ctx, *args, **kwargs):
        access_id = ctx.workspace.settings.SPLIGHT_ACCESS_ID
        secret_key = ctx.workspace.settings.SPLIGHT_SECRET_KEY
        if access_id is None or secret_key is None:
            click.secho(
                "Please set your Splight credentials. Use \"splightcli configure\"",
                fg="red"
            )
            exit(1)
        return f(ctx, *args, **kwargs)
    return wrapper
