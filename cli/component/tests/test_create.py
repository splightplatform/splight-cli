import os
import shutil
from unittest.mock import patch

from cli.component.component import Component
from cli.tests.test_generic import SplightCLITest


class TestCreate(SplightCLITest):
    @patch.object(Component, "_get_random_picture")
    def test_create(self, mock_requests):
        self.path = os.path.join(os.path.dirname(__file__), "test")
        if os.path.exists(self.path):
            shutil.rmtree(self.path)
        os.mkdir(self.path)
        self.component = Component(self.path, self.context)
        self.component.create(self.name, self.version)
        component_path = os.path.join(self.path, f"{self.name}-{self.version}")
        for (dirname, _, filenames) in os.walk(component_path):
            for filename in filenames:
                self.assertTrue(
                    os.path.exists(os.path.join(dirname, filename))
                )
        shutil.rmtree(self.path)

    def test_create_already_exists(self):
        self.path = os.path.join(os.path.dirname(__file__), "test")
        if os.path.exists(self.path):
            shutil.rmtree(self.path)
        os.mkdir(self.path)
        os.mkdir(os.path.join(self.path, f"{self.name}-{self.version}"))
        self.component = Component(self.path, self.context)
        with self.assertRaises(Exception):
            self.component.create(self.name, self.version)
        shutil.rmtree(self.path)
