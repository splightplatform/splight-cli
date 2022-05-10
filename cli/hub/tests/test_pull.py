import os
import shutil
from unittest.mock import patch
from cli.hub.component import Component
from cli.hub.utils import ComponentHandler
from .test_generic import SplightHubTest

class TestPull(SplightHubTest):

    def setUp(self):
        super().setUp()
        self.path = os.path.dirname(os.path.abspath(__file__))

    def test_pull(self):
        self.component = Component(self.path)
        with patch.object(self.component, "exists_in_hub", return_value=True) as exists_in_hub:
            with patch.object(ComponentHandler, "download_component") as downloader:
                self.component.pull(self.name, self.type, self.version)
                exists_in_hub.assert_called_with(self.type, self.name, self.version)
                downloader.assert_called_with(self.type, self.name, self.version, self.path)
    
    def test_pull_already_not_exists_in_hub(self):
        self.component = Component(self.path)
        with patch.object(self.component, "exists_in_hub", return_value=False) as exists_in_hub:
            with patch.object(ComponentHandler, "download_component") as downloader:
                with self.assertRaises(Exception):
                    self.component.pull(self.name, self.type, self.version)
                exists_in_hub.assert_called_with(self.type, self.name, self.version)
                assert not downloader.called

    def test_pull_already_exists_in_local(self):
        self.component = Component(self.path)
        already_component = os.path.join(self.path, f"{self.name}-{self.version}")
        os.mkdir(already_component)
        with self.assertRaises(Exception):
            self.component.pull(self.name, self.type, self.version)
        shutil.rmtree(already_component)

