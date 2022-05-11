import json
from unittest.mock import patch
from cli.hub.component import Component
from .test_generic import SplightHubTest
from io import StringIO

class TestRun(SplightHubTest):

    @patch('sys.stdout', new_callable = StringIO)
    def test_run(self, stdout):
        self.component = Component(self.path)
        run_version = f"{self.name}-{self.version}"
        external_id = "db530a08-5973-4c65-92e8-cbc1d645ebb4"
        namespace = "default"
        run_spec = {
            "name": self.name,
            "type": self.type,
            "version": run_version,
            "parameters": self.parameters,
            "external_id" : external_id,
            "namespace" : namespace
        }
        self.component.run(self.type, json.dumps(run_spec))
        self.assertEqual(stdout.getvalue(), json.dumps(run_spec)+"\n")