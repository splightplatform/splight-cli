from unittest.mock import patch
from cli.constants import *
from cli.engine.datalake import datalake_app
from cli.engine.manager import DatalakeManager
from cli.tests.test_generic import SplightCLITest


class TestLoad(SplightCLITest):

    def setUp(self):
        super().setUp()
        self.expected_load_result = "algo"
        self.configure()

    def test_load(self):
        with patch.object(DatalakeManager, "load", return_value=self.expected_load_result):
            result = self.runner.invoke(datalake_app, ['load', '-p', './dump.csv'], obj=self.context, catch_exceptions=False)
            _ = result.output
