from cli.context import Context
from cli.settings import *
from cli.datalake import list
from cli.utils import RemoteDatalakeHandler
from cli.tests.test_generic import SplightHubTest
from splight_lib.datalake import DatalakeClient
from unittest.mock import patch


class TestList(SplightHubTest):
    def setUp(self):
        super().setUp()
        self.local_collections = ['default', 'default1']
        self.remote_collections = [
            {
                'source': 'default',
                'algorithm': '-'
            },
            {
                'source': 'default1',
                'algorithm': '-'
            }
        ]
        self.set_fake_credentials()

    def test_list(self):
        with patch.object(DatalakeClient, "list_collection_names", return_value=self.local_collections):
            result = self.runner.invoke(list, obj=self.context)
            _stdout = result.output
        self.assertIn("COLLECTION", _stdout)
        self.assertIn("ALGORITHM", _stdout)
        self.assertIn("default", _stdout)
        self.assertIn("default1", _stdout)

    def test_list_remote(self):
        with patch.object(RemoteDatalakeHandler, "list_source", return_value=self.remote_collections):
            result = self.runner.invoke(list, ['--remote'], obj=self.context, catch_exceptions=False)
            _stdout = result.output
        self.assertIn("COLLECTION", _stdout)
        self.assertIn("ALGORITHM", _stdout)
        self.assertIn("default", _stdout)
        self.assertIn("default1", _stdout)