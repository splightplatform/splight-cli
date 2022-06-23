from collections import defaultdict
from email.policy import default
import os
import click
from enum import Enum
from pathlib import Path
from .config import ConfigManager

SPLIGHT_PATH = os.path.join(os.path.expanduser("~"), '.splight')
CONFIG_FILE = os.path.join(SPLIGHT_PATH, 'config')

CONFIG_VARS = {
    "SPLIGHT_ACCESS_ID": {
        "private": True
    },
    "SPLIGHT_SECRET_KEY": {
        "private": True
    },
    "SPLIGHT_HUB_API_HOST": {},
    "SPLIGHT_PLATFORM_API_HOST": {},
}

class PrivacyPolicy(Enum):
    PUBLIC = "public"
    PRIVATE = "private"

class _Context:
    pass


class FakeContext(_Context):
    def __init__(self, **kwargs):
        self.SPLIGHT_ACCESS_ID = None
        self.SPLIGHT_SECRET_KEY = None
        self.SPLIGHT_HUB_API_HOST = 'https://integrationhub.splight-ae.com'
        self.SPLIGHT_PLATFORM_API_HOST = 'https://integrationapi.splight-ae.com'
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        return f"<Context {self.__manager.current_workspace}>"


class Context(_Context):
    def __init__(self):
        self._check_config_file()
        self.__manager = ConfigManager(CONFIG_FILE)
        self.load_workspace()
        self.privacy_policy = PrivacyPolicy.PRIVATE # TODO make this customizable

    @staticmethod
    def _check_config_file():
        if not os.path.exists(CONFIG_FILE):
            os.makedirs(SPLIGHT_PATH, exist_ok=True)
        Path(CONFIG_FILE).touch()

    @property
    def current_workspace(self):
        return self.__manager.current_workspace

    def list_workspaces(self):
        return self.__manager.workspaces

    def switch_workspace(self, workspace_name):
        self.__manager.current_workspace = workspace_name

    def create_workspace(self, workspace_name):
        self.__manager.create_workspace(workspace_name)
        self.__manager.current_workspace = workspace_name

    def delete_workspace(self, workspace_name):
        if self.__manager.current_workspace == workspace_name:
            raise Exception('Move to another workspace first')
        self.__manager.delete_workspace(workspace_name)

    def load_workspace(self):
        [setattr(self, key, self.__manager.workspace.get(key)) for key in CONFIG_VARS]

    def save_workspace(self):
        self.__manager.workspace = {k: getattr(self, k) for k in CONFIG_VARS}

    def __repr__(self):
        return f"<Context {self.__manager.current_workspace}>"


pass_context = click.make_pass_decorator(_Context)