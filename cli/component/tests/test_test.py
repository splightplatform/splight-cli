import os
from cli.component import test
from cli.tests.test_generic import SplightHubTest


class TestTest(SplightHubTest):
    def tearDown(self) -> None:
        for file in [os.path.join(self.path, 'vars.svars'), 'vars.svars']:
            if os.path.exists(file):
                os.remove(file)
        return super().tearDown()

    def test_test(self):
        # parameters input for values just enter for defaults
        _input = "\n".join(["","","","","1","1","1","","1","1","1"])
        result = self.runner.invoke(
            test,
            [self.type, self.path],
            input=_input,
            obj=self.context
        )
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Running component...", result.output)
        # Params required with default
        self.assertIn("Int* [1]: ", result.output)
        self.assertIn("String* [default]: ", result.output)
        self.assertIn("Bool* [True]: ", result.output)
        self.assertIn("Float* [1.0]: ", result.output)
        # Params required without default
        self.assertIn("File*: 1", result.output)
        self.assertIn("Asset*: 1", result.output)
        self.assertIn("Attribute*: 1", result.output)
        self.assertIn("Network*: ", result.output)
        ## Retry if value not provided
        self.assertIn("Network*: 1", result.output)
        # Params non required without default
        self.assertIn("Algorithm [None]: 1", result.output)
        self.assertIn("Connector [None]: 1", result.output)