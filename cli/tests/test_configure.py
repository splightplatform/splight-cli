from unittest.mock import patch
from cli.cli import component
from cli.tests.test_generic import SplightCLITest
from cli.constants import *
from cli.component.handler import ComponentHandler


class TestConfigure(SplightCLITest):

    def test_configure_requested(self):
        result = self.runner.invoke(
            component,
            ["list"],
            obj=self.context,
            catch_exceptions=False
        )
        self.assertEqual(result.exit_code, 1)
        self.assertIn("splightcli configure", result.output)

    def test_configure_not_requested(self):
        self.configure()
        with patch.object(ComponentHandler, "list_components", return_value=[]):
            result = self.runner.invoke(
                component,
                ["list"],
                obj=self.context,
                catch_exceptions=False
            )
        self.assertEqual(result.exit_code, 0)
        self.assertIn('NAME', result.output)
