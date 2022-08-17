from unittest.mock import patch
from cli.constants import *
from cli.datalake import load
from cli.datalake.datalake import Datalake
from cli.tests.test_generic import SplightCLITest


class TestLoad(SplightCLITest):

    def setUp(self):
        super().setUp()
        self.expected_load_result = "algo"
        self.configure()

    def test_load(self):
        with patch.object(Datalake, "load", return_value=self.expected_load_result):
            result = self.runner.invoke(load, obj=self.context, catch_exceptions=False)
            _ = result.output
    
    def test_load_example(self):
        pass