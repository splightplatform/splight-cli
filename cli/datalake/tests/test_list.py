from cli.constants import *
from cli.datalake.datalake import Datalake
from cli.tests.test_generic import SplightCLITest
from cli.datalake import list
from unittest.mock import patch



class TestList(SplightCLITest):
    def setUp(self):
        super().setUp()
        self.remote_collections = [
            {
                'source': 'default',
                'component': '-'
            },
            {
                'source': 'default1',
                'component': '-'
            }
        ]
        self.configure()

    def test_list(self):
        with patch.object(Datalake, "list", return_value=self.remote_collections):
            result = self.runner.invoke(list, obj=self.context, catch_exceptions=False)
            _stdout = result.output
        self.assertIn("COLLECTION_NAME", _stdout)
        self.assertIn("default", _stdout)
        self.assertIn("default1", _stdout)