import os
from cli.context import CONFIG_FILE, Context
from unittest import TestCase
from ...settings import *
from cli.datalake.datalake import Datalake
import json
from cli.utils import BASE_DIR

class TestDump(TestCase):

    def setUp(self):
        self.context = Context()
        self.namespace = 'default'
        self.collection = 'qw298nCUIS38b2DUMP'
        self.path = os.path.join(os.path.dirname(__file__), "dump_data.csv")
        self.datalake_path = os.path.expanduser(f"~/.splight/datalake")
        self.collection_path = os.path.expanduser(f"~/.splight/datalake/{self.collection}")
        self.dump_example_path = f"{BASE_DIR}/cli/datalake/dump_example.csv"
        self.write_data = [
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
                "instance_id": None,
                "instance_type": None,
                "path": "2/10",
                "timestamp": "2020-10-10 00:00:00"
            },
        ]
        self.expected_dump = "path,asset_id,attribute_id,instance_id,instance_type,timestamp,f,p,q,r,s\n2/10,052fb43e-21f3-4503-a7da-fe9455d89b03,2,,,2020-10-10,0,1,2,3,4\n"
        os.makedirs(self.datalake_path, exist_ok=True)
        with open(self.collection_path, 'w+') as f:
            json.dump(self.write_data, f)

    def tearDown(self) -> None:
        if os.path.exists(self.path):
            os.remove(self.path)
        if os.path.exists(self.collection_path):
            os.remove(self.collection_path)
        return super().tearDown()

    def test_dump(self):
        d = Datalake(self.context, self.namespace)
        d.dump(path=self.path,
               collection=self.collection,
               filter=[],
               remote=False,
               example=False)
        with open(self.path) as f:
            self.assertEqual(f.read(), self.expected_dump)

    def test_dump_example(self):
        d = Datalake(self.context, self.namespace)
        d.dump(path=self.path,
               collection=self.collection, 
               filter=[],
               remote=False,
               example=True)
        with open(self.path) as f:
            ff = open(self.dump_example_path, 'r')
            self.assertEqual(f.read(), ff.read())
            ff.close()
