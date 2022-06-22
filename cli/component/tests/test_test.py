import os
from click.testing import CliRunner
from cli.component import test
from .test_generic import SplightHubTest


class TestTest(SplightHubTest):
    def setUp(self):
        self.runner = CliRunner()
        return super().setUp()

    def tearDown(self) -> None:
        for file in [os.path.join(self.path, 'vars.svars'), 'vars.svars']:
            if os.path.exists(file):
                os.remove(file)
        return super().tearDown()

    def test_test(self):
        # parameters input for values just enter for defaults
        _input = "\n".join(["","","","","1","1","1","1","1","1"])
        result = self.runner.invoke(
            test,
            [self.type, self.path],
            input=_input,
            obj=self.context
        )
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Running component...", result.output)
        self.assertIn("File: 1", result.output)
        self.assertIn("Asset: 1", result.output)
        self.assertIn("Attribute: 1", result.output)
        self.assertIn("Network: 1", result.output)
        self.assertIn("Algorithm: 1", result.output)
        self.assertIn("Connector: 1", result.output)