import json
import re

from cli.component import component_app
from cli.component.component import Component
from cli.tests.test_generic import SplightCLITest


class TestRun(SplightCLITest):
    def test_run(self):
        self.component = Component(self.context)
        self.configure()
        result = self.runner.invoke(
            component_app,
            ["run", self.path, "--input", json.dumps(self.input)],
            obj=self.context,
            catch_exceptions=False,
        )
        # Remove ANSI characters that prints with color
        ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
        output = ansi_escape.sub("", result.output)
        self.assertEqual(
            output,
            "Running component...\nHELLO\nHELLO2\n",
        )
