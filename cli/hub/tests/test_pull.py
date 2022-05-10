import os
import requests
import shutil
from unittest.mock import patch
from cli.hub.component import Component
from cli.hub.utils import ComponentHandler
from .test_generic import SplightHubTest
from ..settings import *

class TestPull(SplightHubTest):

    def setUp(self):
        super().setUp()
        self.original_component_path = self.path
        self.path = os.path.dirname(os.path.abspath(__file__))
        self.extracted_component_path = os.path.join(self.path, f"{self.name}-{self.version}")
        self.component = Component(self.path)

    def test_pull(self):
        with patch.object(self.component, "exists_in_hub", return_value=True) as exists_in_hub:
            with patch.object(ComponentHandler, "download_component") as downloader:
                self.component.pull(self.name, self.type, self.version)
                exists_in_hub.assert_called_with(self.type, self.name, self.version)
                downloader.assert_called_with(self.type, self.name, self.version, self.path)
    
    def test_pull_already_not_exists_in_hub(self):
        with patch.object(self.component, "exists_in_hub", return_value=False) as exists_in_hub:
            with patch.object(ComponentHandler, "download_component") as downloader:
                with self.assertRaises(Exception):
                    self.component.pull(self.name, self.type, self.version)
                exists_in_hub.assert_called_with(self.type, self.name, self.version)
                assert not downloader.called

    def test_pull_already_exists_in_local(self):
        already_component = os.path.join(self.path, f"{self.name}-{self.version}")
        os.mkdir(already_component)
        with self.assertRaises(Exception):
            self.component.pull(self.name, self.type, self.version)
        shutil.rmtree(already_component)
    
    def test_component_download(self):
        headers = {
            #'Authorization': token
        }
        data = {
            'type': self.type,
            'name': self.name,
            'version': self.version,
        }
        with patch.object(self.component, "exists_in_hub", return_value=True):
            compressed_filename = f"{self.name}-{self.version}.{COMPRESSION_TYPE}"
            file = None
            with open(os.path.join(self.original_component_path, compressed_filename), "rb") as f:
                file = f.read()
            response = requests.Response()
            response.status_code = 200
            response._content = file
            with patch.object(requests, "post", return_value=response) as post:
                os.chdir(self.path)
                self.component.pull(self.name, self.type, self.version)
                _, args, kwargs = post.mock_calls[0]
                self.assertEqual(args[0], f"{API_URL}/download")
                self.assertEqual(kwargs["data"], data)
                self.assertEqual(kwargs["headers"], headers)
                self.assertTrue(os.path.exists(self.extracted_component_path))


