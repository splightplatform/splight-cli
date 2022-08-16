from unittest.mock import patch
from cli.constants import *
from cli.datalake import dump
from cli.datalake.datalake import Datalake
from cli.tests.test_generic import SplightCLITest


class TestDump(SplightCLITest):

    def setUp(self):
        super().setUp()
        self.configure()

    def test_dump(self):
        with patch.object(Datalake, "dump") as mocked_dump:
            result = self.runner.invoke(dump, ['--path', 'dump.csv'], obj=self.context, catch_exceptions=False)
            self.assertEqual(result.output, '')
            mocked_dump.assert_called_once()

    def test_dump_example(self):
        pass
