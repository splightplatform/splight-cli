from pathlib import Path
from typing import List

from cli.constants import (
    CONFIG_FILE,
    DEFAULT_WORKSPACE,
    DEFAULT_WORKSPACE_NAME,
    DEFAULT_WORKSPACES,
)
from cli.settings import SplightCLIConfig, SplightCLISettings
from cli.utils.yaml import get_yaml_from_file, save_yaml_to_file


class WorkspaceDeleteError(Exception):
    def __init__(self, workspace: str):
        self._msg = (
            f"Workspace '{workspace}' is your active workspace\n\n"
            "You cannot delete the currently active workspace"
        )

    def __str__(self) -> str:
        return self._msg


class NotExistingWorkspace(Exception):
    def __init__(self, workspace: str):
        self._msg = f"Workspace {workspace} does not exist in your environment"

    def __str__(self) -> str:
        return self._msg


class WorkspaceManager:
    def __init__(self):
        self.config_file = CONFIG_FILE
        path = Path(self.config_file)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch()
        self._config = self.__load_config()
        self._workspaces = self._config.workspaces
        self._current_workspace = self._config.current_workspace
        self._settings = self._workspaces[self._current_workspace]

    def __load_config(self):
        config = get_yaml_from_file(self.config_file)
        # Default values
        config["workspaces"] = config.get("workspaces", DEFAULT_WORKSPACES)
        workspace_name = config.get(
            "current_workspace", DEFAULT_WORKSPACE_NAME
        )
        if workspace_name not in config["workspaces"]:
            workspace_name = (
                DEFAULT_WORKSPACE_NAME
                if DEFAULT_WORKSPACE_NAME in config["workspaces"]
                else list(config["workspaces"].keys())[0]
            )
        config["current_workspace"] = workspace_name
        save_yaml_to_file(config, self.config_file)
        config = SplightCLIConfig.parse_obj(config)
        return config

    @property
    def settings(self) -> SplightCLISettings:
        return self._settings

    @property
    def current_workspace(self) -> str:
        return self._current_workspace

    def update_workspace(self, new_settings: SplightCLISettings):
        self._workspaces[self._current_workspace] = new_settings
        save_yaml_to_file(self._config.dict(), self.config_file)

    def select_workspace(self, workspace_name: str):
        if workspace_name not in self._workspaces:
            raise NotExistingWorkspace(workspace_name)
        self._config.current_workspace = workspace_name
        save_yaml_to_file(self._config.dict(), self.config_file)

    def list_workspaces(self) -> List[str]:
        return [
            f"{key}*" if key == self._current_workspace else f"{key}"
            for key in self._config.workspaces.keys()
        ]

    def delete_workspace(self, workspace_name: str):
        if workspace_name not in self._config.workspaces:
            raise Exception("Not a valid namespace name")

        if workspace_name == self._current_workspace:
            raise WorkspaceDeleteError(workspace_name)
        del self._config.workspaces[workspace_name]
        save_yaml_to_file(self._config.dict(), self.config_file)

    def create_workspace(self, workspace_name: str):
        if workspace_name in self._config.workspaces:
            raise Exception("Name already exists")
        self._config.workspaces.update({workspace_name: DEFAULT_WORKSPACE})
        self._config.current_workspace = workspace_name
        self._current_workspace = workspace_name
        save_yaml_to_file(self._config.dict(), self.config_file)
