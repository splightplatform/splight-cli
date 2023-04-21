import json
import os
import re
from unittest.mock import patch

from cli.component import component_app
from cli.component.component import Component
from cli.tests.test_generic import SplightCLITest

os.environ["SPLIGHT_ACCESS_ID"] = "access_id"
os.environ["SPLIGHT_SECRET_KEY"] = "secret_key"


class TestRun(SplightCLITest):
    @patch.object(Component, "_validate_cli_version", return_value=None)
    @patch(
        "splight_lib.client.datalake.RemoteDatalakeClient.create_index",
        return_value=None,
    )
    def test_run(self, mock, mock1):
        self.component = Component(self.context)
        self.configure()
        result = self.runner.invoke(
            component_app,
            ["run", self.path, "--input", json.dumps(self.input)],
            obj=self.context,
            catch_exceptions=False,
        )
        # Remove ANSI characters that prints with color
        mock1.assert_called_once()
        ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
        output = ansi_escape.sub("", result.output)
        self.assertEqual(
            output,
            "Running component...\nHELLO\nHELLO2\n",
        )
