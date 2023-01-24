from unittest.mock import patch

from cli.cli import component_app

from cli.component.handler import ComponentHandler
from cli.tests.test_generic import SplightCLITest


class TestConfigure(SplightCLITest):
    def test_configure_requested(self):
        with patch.object(
            ComponentHandler, "list_components", return_value=[]
        ):
            result = self.runner.invoke(
                component_app,
                ["list"],
                obj=self.context,
                catch_exceptions=False,
            )
        self.assertEqual(result.exit_code, 1)
        self.assertIn("splight configure", result.output)

    def test_configure_not_requested(self):
        self.configure()
        with patch.object(
            ComponentHandler, "list_components", return_value=[]
        ):
            result = self.runner.invoke(
                component_app,
                ["list"],
                obj=self.context,
                catch_exceptions=False,
            )
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Name", result.output)
