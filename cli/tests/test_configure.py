import re
from unittest.mock import patch

# from cli.hub.component import component_app
from cli.hub import hub_app
from cli.hub.component.hub_manager import HubComponentManager

# from cli.component.handler import ComponentHandler
from cli.tests.test_generic import SplightCLITest


class TestConfigure(SplightCLITest):
    def test_configure_requested(self):
        with patch.object(
            HubComponentManager, "list_components", return_value=None
        ):
            result = self.runner.invoke(
                hub_app,
                ["component", "list"],
                obj=self.context,
                catch_exceptions=False,
            )
        ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
        output = ansi_escape.sub("", result.output)
        self.assertEqual(result.exit_code, 1)
        self.assertIn("splight configure", output)

    def test_configure_not_requested(self):
        self.configure()
        with patch.object(
            HubComponentManager, "list_components", return_value=None
        ):
            result = self.runner.invoke(
                hub_app,
                ["component", "list"],
                obj=self.context,
                catch_exceptions=False,
            )
        self.assertEqual(result.exit_code, 0)
