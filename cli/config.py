from .utils.yaml import get_yaml_from_file, save_yaml_to_file


class ConfigManager:
    DEFAULT_CURRENT_WORKSPACE = 'default'
    DEFAULT_WORKSPACE = {
        'SPLIGHT_HUB_API_HOST': 'https://hub.splight-ae.com',
        'SPLIGHT_PLATFORM_API_HOST': 'https://api.splight-ae.com',
    }
    DEFAULT_WORKSPACES = {
        DEFAULT_CURRENT_WORKSPACE: DEFAULT_WORKSPACE
    }

    def __init__(self, config_file: str):
        self.config_file = config_file
        self._config = self.__load_config()

    def __load_config(self):
        config = get_yaml_from_file(self.config_file)
        # Default values
        config['workspaces'] = config.get('workspaces', self.DEFAULT_WORKSPACES)
        config['current_workspace'] = config.get('current_workspace', self.DEFAULT_CURRENT_WORKSPACE)
        save_yaml_to_file(config, self.config_file)
        return config

    @property
    def current_workspace(self):
        return self._config.get('current_workspace')

    @current_workspace.setter
    def current_workspace(self, value):
        self._config['current_workspace'] = value
        save_yaml_to_file(self._config, self.config_file)

    @property
    def workspace(self):
        workspaces = self._config.get('workspaces')
        return workspaces.get(self.current_workspace)

    @workspace.setter
    def workspace(self, value: dict):
        workspace = self.workspace
        workspace.update(value)
        self._config['current_workspace'] = self.current_workspace
        save_yaml_to_file(self._config, self.config_file)

    @property
    def workspaces(self):
        workspaces = self._config.get('workspaces').keys()
        return [f"{key}*" if key == self.current_workspace else f"{key}" for key in workspaces]

    def delete_workspace(self, workspace_name):
        if workspace_name not in self._config['workspaces']:
            raise Exception('Not a valid namespace name')
        del self._config['workspaces'][workspace_name]
        save_yaml_to_file(self._config, self.config_file)

    def create_workspace(self, workspace_name):
        if workspace_name in self._config['workspaces']:
            raise Exception('Name already exists')
        self._config['workspaces'].update({workspace_name: self.DEFAULT_WORKSPACE})
        self.current_workspace = workspace_name
        save_yaml_to_file(self._config, self.config_file)
