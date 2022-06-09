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
        self.collection_load = 'qw298nCUIS38b2LOAD1'
        self.collection_example = 'qw298nCUIS38b2LOAD2'
        self.collection_path_load = os.path.expanduser(f"~/.splight/datalake/{self.collection_load}")
        self.collection_path_example = os.path.expanduser(f"~/.splight/datalake/{self.collection_example}")
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
            }
        ]
        self.expected_example_output = [
            {
                "args": {
                    "f": 0,
                    "p": 1,
                    "q": 2,
                    "r": 3,
                    "s": 4
                },
                "asset_id": "052fb43e-21f3-4503-a7da-fe9455d89b03",
                "attribute_id": "h80fb43e-21f3-4503-a7da-fe9455d89b03",
                "path": "2/10",
                "timestamp": "2020-10-10 00:00:00"
            } 
            for i in range(5)
        ]


    def test_load(self):
        d = Datalake(self.context, self.namespace)
        d.load(collection=self.collection_load, path=self.path, example=False)
        with open(self.collection_path_load) as f:
            read = json.loads(f.read())
        os.remove(self.collection_path_load)
        self.assertEqual(read, self.expected_output)
    
    def test_load_example(self):
        d = Datalake(self.context, self.namespace)
        d.load(collection=self.collection_example, path=None, example=True)
        with open(self.collection_path_example) as f:
            read = json.loads(f.read())
        os.remove(self.collection_path_example)
        self.assertEqual(read, self.expected_example_output)