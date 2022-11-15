from pathlib import Path
from typing import Dict, List
from cli.settings import SplightCLISettings
from cli.utils.yaml import get_yaml_from_file, save_yaml_to_file
from cli.constants import CONFIG_FILE, DEFAULT_WORKSPACE, DEFAULT_WORKSPACE_NAME, DEFAULT_WORKSPACES


class WorkspaceDeleteError(Exception):
    def __init__(self, workspace: str):
        self._msg = (
            f"Workspace '{workspace}' is your active workspace\n\n"
            "You cannot delete the currently active workspace"
        )

    def __str__(self) -> str:
        return self._msg


class WorkspaceManager:
    def __init__(self):
        self.config_file = CONFIG_FILE
        Path(self.config_file).touch()
        self._settings = self.__load_config()
        self._workspaces: List[Dict] = self._settings.get('workspaces')
        self._current_workspace: str = self._settings.get('current_workspace')
        self._current_settings = SplightCLISettings.parse_obj(self._workspaces[self._current_workspace])

    def __load_config(self):
        config = get_yaml_from_file(self.config_file)
        # Default values
        config['workspaces'] = config.get('workspaces', DEFAULT_WORKSPACES)
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
        return config

    @property
    def settings(self):
        return self._current_settings

    @property
    def current_workspace(self):
        return self._current_workspace

    def update_workspace(self, new_settings):
        self._workspaces[self._current_workspace] = new_settings.dict()
        save_yaml_to_file(self._settings, self.config_file)

    def select_workspace(self, value):
        self._settings['current_workspace'] = value
        save_yaml_to_file(self._settings, self.config_file)

    def list_workspaces(self):
        workspaces = self._settings.get('workspaces').keys()
        return [f"{key}*" if key == self._current_workspace else f"{key}" for key in workspaces]

    def delete_workspace(self, workspace_name):
        if workspace_name not in self._settings['workspaces']:
            raise Exception('Not a valid namespace name')

        if workspace_name == self._current_workspace:
            raise WorkspaceDeleteError(workspace_name)
        del self._settings['workspaces'][workspace_name]
        save_yaml_to_file(self._settings, self.config_file)

    def create_workspace(self, workspace_name):
        if workspace_name in self._settings['workspaces']:
            raise Exception('Name already exists')
        self._settings['workspaces'].update({
            workspace_name: DEFAULT_WORKSPACE
        })
        self._settings['current_workspace'] = workspace_name
        self._current_workspace = workspace_name
        save_yaml_to_file(self._settings, self.config_file)
