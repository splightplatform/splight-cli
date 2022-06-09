import os
from cli.context import CONFIG_FILE, Context
from unittest import TestCase
from ...settings import *
from cli.datalake.datalake import Datalake
import json

class TestLoad(TestCase):

    def setUp(self):
        self.context = Context()
        self.namespace = 'default'
        self.collection = 'qw298nCUIS38b2LOAD'
        self.collection_path = os.path.expanduser(f"~/.splight/datalake/{self.collection}")
        self.path = os.path.join(os.path.dirname(__file__), "load_example.csv")
        self.expected_output = [
            {
                "args": {
                    "f": 0,
                    "p": 1,
                    "q": 2,
                    "r": 3,
                    "s": 4
                },
                "asset_id": "052fb43e-21f3-4503-a7da-fe9455d89b03",
                "attribute_id": "2",
                "path": "2/10",
                "timestamp": "2020-10-10 00:00:00"
            },
        ]

    def test_load(self):
        d = Datalake(self.context, self.namespace)
        d.load(collection=self.collection, path=self.path)
        with open(self.collection_path) as f:
            self.assertEqual(json.loads(f.read()), self.expected_output)
        os.remove(self.collection_path)
        