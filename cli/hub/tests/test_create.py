import os
import shutil
from unittest.mock import patch
from cli.hub.component import Component
from cli.hub.utils import ComponentHandler
from .test_generic import SplightHubTest

class TestCreate(SplightHubTest):

    def test_create(self):
        self.path = os.path.join(os.path.dirname(__file__), "test")
        os.mkdir(self.path)
        self.component = Component(self.path)
        self.component.create(self.name, self.type, self.version)
        component_path = os.path.join(self.path, f"{self.name}-{self.version}")
        for (dirname, _, filenames) in os.walk(component_path):
            for filename in filenames:
                self.assertTrue(os.path.exists(os.path.join(dirname, filename)))
        shutil.rmtree(self.path)

    def test_create_already_exists(self):
        self.path = os.path.join(os.path.dirname(__file__), "test")
        os.mkdir(self.path)
        os.mkdir(os.path.join(self.path, f"{self.name}-{self.version}"))
        self.component = Component(self.path)
        with self.assertRaises(Exception):
            self.component.create(self.name, self.type, self.version)
        shutil.rmtree(self.path)

