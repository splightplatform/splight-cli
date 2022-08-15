import click
from enum import Enum
from cli.context.workspace import WorkspaceManager
from cli.context.framework import FrameworkManager


class PrivacyPolicy(Enum):
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