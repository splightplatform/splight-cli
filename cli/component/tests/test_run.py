import os
from unittest.mock import patch

from splight_lib.execution import ExecutionClient

from cli.component.component import Component
from cli.tests.test_generic import SplightCLITest

os.environ["SPLIGHT_ACCESS_ID"] = "access_id"
os.environ["SPLIGHT_SECRET_KEY"] = "secret_key"


class TestRun(SplightCLITest):
    @patch.object(ExecutionClient, "start", return_value=None)
    @patch(
        "splight_lib.component.abstract.AbstractComponent._check_duplicated_component",
        return_value=None,
    )
    @patch.object(Component, "_validate_cli_version", return_value=None)
    @patch(
        "splight_lib.client.datalake.RemoteDatalakeClient.create_index",
        return_value=None,
    )
    def test_run(self, mock, mock1, mock2, mock3):
        # TODO: Change this tests
        self.component = Component(self.context)
        self.component.run(self.path, self.input)
