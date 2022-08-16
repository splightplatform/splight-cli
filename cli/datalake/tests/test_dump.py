from unittest.mock import patch
from cli.constants import *
from cli.datalake import dump
from cli.datalake.datalake import Datalake
from cli.tests.test_generic import SplightCLITest


class TestDump(SplightCLITest):

    def setUp(self):
        super().setUp()
        self.expected_dump = "algo"
        self.configure()

    def test_dump(self):
        with patch.object(Datalake, "dump", return_value=self.expected_dump):
            result = self.runner.invoke(dump, obj=self.context, catch_exceptions=False)
            _ = result.output

        with open(self.path) as f:
            self.assertEqual(f.read(), self.expected_dump)

    def test_dump_example(self):
        pass
