import json

from cli.component import run
from cli.component.component import Component
from cli.constants import DEFAULT_EXTERNAL_ID, DEFAULT_NAMESPACE
from cli.tests.test_generic import SplightCLITest


class TestRun(SplightCLITest):
    def test_run(self):
        self.component = Component(self.path, self.context)
        run_version = f"{self.name}-{self.version}"
        external_id = DEFAULT_EXTERNAL_ID
        namespace = DEFAULT_NAMESPACE
        run_spec = {
            "name": self.name,
            "type": self.type,
            "version": run_version,
            "parameters": self.parameters,
            "external_id": external_id,
            "namespace": namespace,
        }
        self.configure()
        result = self.runner.invoke(
            run,
            [self.type, self.path, "--run-spec", json.dumps(run_spec)],
            obj=self.context,
            catch_exceptions=False,
        )
        self.assertEqual(
            result.output, "Running component...\nHELLO\nHELLO2\n"
        )
