from cli.context import Context
from unittest import TestCase
from ...settings import *
from cli.datalake.datalake import Datalake
from splight_lib.datalake import DatalakeClient
from cli.utils import RemoteDatalakeHandler
from unittest.mock import patch
from io import StringIO

class TestList(TestCase):

    def setUp(self):
        self.context = Context()
        self.collection_names = ['default', 'default1']
        self.list_remote_source = [
            {
                'source': 'default',
                'algo': '-'
            },
            {
                'source': 'default1',
                'algo': '-'
            }
        ]
        self.namespace = 'default'
        self.out_format = "{:<50} {:<15}\n"

    @patch('sys.stdout', new_callable = StringIO)
    def test_list(self, stdout):
        with patch.object(DatalakeClient, "list_collection_names", return_value=self.collection_names) as col_names:
            d = Datalake(self.context, self.namespace)
            d.list(remote=False)
            expected_output = self.out_format.format("COLLECTION", "ALGORITHM")
            for col in self.collection_names:
                expected_output += self.out_format.format(col, "-")
            self.assertEqual(stdout.getvalue(), expected_output)

    @patch('sys.stdout', new_callable = StringIO)
    def test_list_remote(self, stdout):
        with patch.object(RemoteDatalakeHandler, "list_source", return_value=self.list_remote_source) as col_names:
            d = Datalake(self.context, self.namespace)
            d.list(remote=True)
            expected_output = self.out_format.format("COLLECTION", "ALGORITHM")
            for col in self.list_remote_source:
                expected_output += self.out_format.format(col['source'], col['algo'])
            self.assertEqual(stdout.getvalue(), expected_output)