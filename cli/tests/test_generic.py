import os
from unittest import TestCase
# from click.testing import CliRunner
from typer.testing import CliRunner
from splight_lib.settings import setup

from cli.component.spec import Spec
from cli.constants import DEFAULT_WORKSPACE, SPEC_FILE
from cli.context import Context
from cli.settings import SplightCLISettings
from cli.utils import get_json_from_file


class FakeFramework:
    @property
    def setup(self):
        return setup

    def configure(self, environment):
        # empty_keys = [
        #     key for key, value in environment.items() if value is None
        # ]
        setup.configure(environment)


class FakeWorkspace:
    _current_workspace = "test"
    _workspaces = {"test": DEFAULT_WORKSPACE}

    def __init__(self):
        self._current_settings = SplightCLISettings.parse_obj(self._workspaces[self._current_workspace])

    @property
    def settings(self):
        return self._current_settings

    @property
    def current_workspace(self):
        return self._current_workspace

    def update_workspace(self, new_settings):
        self._current_settings = SplightCLISettings.parse_obj(new_settings.dict())

    def select_workspace(self, value):
        self._current_workspace = value

    def list_workspaces(self):
        workspaces = self._workspaces.keys()
        return [f"{key}*" if key == self._current_workspace else f"{key}" for key in workspaces]

    def delete_workspace(self, workspace_name):
        if workspace_name not in self._workspaces:
            raise Exception('Not a valid namespace name')
        del self._workspaces[workspace_name]

    def create_workspace(self, workspace_name):
        if workspace_name in self._workspaces:
            raise Exception('Name already exists')
        self._workspaces.update({
            workspace_name: DEFAULT_WORKSPACE
        })
        self._current_workspace = workspace_name


class FakeContext(Context):
    def __init__(self):
        self.__workspace = FakeWorkspace()
        self.__framework = FakeFramework()

    @property
    def framework(self):
        self.__framework.configure(self.workspace.settings.dict())
        return self.__framework

    @property
    def workspace(self):
        return self.__workspace

    def __repr__(self):
        return f"<Context {self.__workspace}>"


class SplightCLITest(TestCase):

    def setUp(self):
        self.path = os.path.join(os.path.dirname(__file__), "TestHub")
        self.component_json = get_json_from_file(os.path.join(self.path, SPEC_FILE))
        self.spec = Spec.parse_obj(self.component_json)
        self.name = self.component_json['name']
        self.version = self.component_json['version']
        self.splight_cli_version = self.component_json['splight_cli_version']
        self.component_type = self.component_json['component_type']
        self.privacy_policy = self.component_json['privacy_policy']
        self.component_id = self.component_json["component_id"]
        self.custom_types = self.component_json['custom_types']
        self.input = self.component_json['input']
        self.output = self.component_json['output']
        self.bindings = self.component_json["bindings"]
        self.tags = self.component_json['tags']
        self.commands = self.component_json['commands']
        self.endpoints = self.component_json['endpoints']
        self.context = FakeContext()
        self.runner = CliRunner()

    @property
    def default_configuration(self):
        return SplightCLISettings.parse_obj({
            "SPLIGHT_ACCESS_ID": "access_id",
            "SPLIGHT_SECRET_KEY": "secret_key",
            "DATABASE_CLIENT": "fake_splight_lib.database.FakeDatabaseClient",
            "HUB_CLIENT": "fake_splight_lib.hub.FakeHubClient",
            "DATALAKE_CLIENT": "fake_splight_lib.datalake.FakeDatalakeClient",
            "DEPLOYMENT_CLIENT": "fake_splight_lib.deployment.FakeDeploymentClient",
        })

    def configure(self):
        self.context.workspace.update_workspace(self.default_configuration)

    def tearDown(self) -> None:
        return super().tearDown()
