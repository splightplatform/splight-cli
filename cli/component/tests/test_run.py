import json

from cli.component import run
from cli.component.component import Component
from cli.tests.test_generic import SplightCLITest


class TestRun(SplightCLITest):
    def test_run(self):
        self.component = Component(self.context)
        self.configure()
        result = self.runner.invoke(
            run,
            [self.path, "--input", json.dumps(self.input)],
            obj=self.context,
            catch_exceptions=False,
        )
        self.assertEqual(
            result.output, "Running component...\nHELLO\nHELLO2\n"
        )
