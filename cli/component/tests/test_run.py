import json

from cli.component import run
from cli.component.component import Component
from cli.constants import DEFAULT_COMPONENT_ID, DEFAULT_NAMESPACE
from cli.tests.test_generic import SplightCLITest


class TestRun(SplightCLITest):
    def test_run(self):
        self.component = Component(self.path, self.context)
        run_version = f"{self.name}-{self.version}"
        component_id = DEFAULT_COMPONENT_ID
        namespace = DEFAULT_NAMESPACE
        run_spec = {
            "name": self.name,
            "version": self.version,
            "tags": self.tags,
            "custom_types": self.custom_types,
            "input": self.input,
            "output": self.output,
        }
        self.configure()
        result = self.runner.invoke(
            run,
            [self.path, "--run-spec", json.dumps(run_spec)],
            obj=self.context,
            catch_exceptions=False,
        )
        self.assertEqual(
            result.output, "Running component...\nHELLO\nHELLO2\n"
        )
