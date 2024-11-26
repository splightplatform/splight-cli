import os
from pathlib import Path
from typing import List

from splight_cli.constants import (
    CONFIG_FILE,
    DEFAULT_WORKSPACE,
    DEFAULT_WORKSPACE_NAME,
    DEFAULT_WORKSPACES,
)
from splight_cli.settings import SplightCLIConfig, SplightCLISettings
from splight_cli.utils.yaml import get_yaml_from_file, save_yaml_to_file


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


class ConfigurationError(Exception):
    pass


class WorkspaceManager:
    def __init__(self, new_workspace: bool = False):
        self.config_file = CONFIG_FILE
        self._config = self.__load_config()
        self._workspaces = self._config.workspaces
        self._current_workspace = self._config.current_workspace
        self._settings = self._workspaces[self._current_workspace]
        if not self._settings.is_configured() and not new_workspace:
            raise ConfigurationError(
                (
                    "There is at least one variable missing. "
                    "Use command 'splight configure'"
                )
            )

    def __load_config(self):
        try:
            if os.path.exists(self.config_file):
                config = self._load_from_file(self.config_file)
            else:
                config = self._load_from_env()
        except Exception as exc:
            raise ConfigurationError(
                "An error ocurred while loading configuration"
            ) from exc
        return config

    def _load_from_file(self, file_path: str) -> SplightCLIConfig:
        config = get_yaml_from_file(file_path)
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
        save_yaml_to_file(config, file_path)
        config = SplightCLIConfig.model_validate(config)
        return config

    def _load_from_env(self) -> SplightCLIConfig:
        config = SplightCLIConfig(
            current_workspace=DEFAULT_WORKSPACE_NAME,
            workspaces=DEFAULT_WORKSPACES,
        )
        path = Path(self.config_file)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch()
        save_yaml_to_file(config.model_dump(), self.config_file)
        return config

    @property
    def settings(self) -> SplightCLISettings:
        return self._settings

    @property
    def current_workspace(self) -> str:
        return self._current_workspace

    def update_workspace(self, new_settings: SplightCLISettings):
        self._workspaces[self._current_workspace] = new_settings
        save_yaml_to_file(self._config.model_dump(), self.config_file)

    def select_workspace(self, workspace_name: str):
        if workspace_name not in self._workspaces:
            raise NotExistingWorkspace(workspace_name)
        self._config.current_workspace = workspace_name
        save_yaml_to_file(self._config.model_dump(), self.config_file)

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
        save_yaml_to_file(self._config.model_dump(), self.config_file)

    def create_workspace(self, workspace_name: str):
        if workspace_name in self._config.workspaces:
            raise Exception("Name already exists")
        self._config.workspaces.update({workspace_name: DEFAULT_WORKSPACE})
        self._config.current_workspace = workspace_name
        self._current_workspace = workspace_name
        save_yaml_to_file(self._config.model_dump(), self.config_file)

    def list_workspace_contents(self, workspace_name: str):
        if workspace_name not in self._config.workspaces:
            raise NotExistingWorkspace(workspace_name)
        return self._config.workspaces[workspace_name]
