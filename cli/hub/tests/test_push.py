import os
import requests
import py7zr
import json
from unittest.mock import patch
from cli.hub.component import Component, ComponentAlreadyExistsException
from cli.hub.utils import ComponentHandler
from .test_generic import SplightHubTest
from ..settings import *

class TestPush(SplightHubTest):

    def setUp(self):
        super().setUp()
        self.component = Component(self.path)

    def test_push(self):
        with patch.object(self.component, "exists_in_hub", return_value=False) as exists_in_hub:
            with patch.object(ComponentHandler, "upload_component") as uploader:
                self.component.push(self.type, force=False)
                exists_in_hub.assert_called_with(self.type, self.name, self.version)
                uploader.assert_called_with(self.type, self.name, self.version, self.parameters, self.path)
    
    def test_push_already_exists(self):
        with patch.object(self.component, "exists_in_hub", return_value=True) as exists_in_hub:
            with patch.object(ComponentHandler, "upload_component") as uploader:
                with self.assertRaises(ComponentAlreadyExistsException):
                    self.component.push(self.type, force=False)
                exists_in_hub.assert_called_with(self.type, self.name, self.version)

    def test_push_forced(self):
        with patch.object(ComponentHandler, "upload_component") as uploader:
            self.component.push(self.type, force=True)
            uploader.assert_called_with(self.type, self.name, self.version, self.parameters, self.path)
        
    def test_component_upload(self):
        headers = {
            #'Authorization': token
        }
        data = {
            'type': self.type,
            'name': self.name,
            'version': self.version,
            'parameters': json.dumps(self.parameters),
        }

        with patch.object(self.component, "exists_in_hub", return_value=False):
            response = requests.Response()
            response.status_code = 201
            with patch.object(requests, "post", return_value=response) as post:
                with patch.object(py7zr.SevenZipFile, "writeall") as writeall:
                    self.component.push(self.type, force=False)

                    writeall.assert_called_with(self.path, f"{self.name}-{self.version}")

                    compressed_filename = f"{self.name}-{self.version}.{COMPRESSION_TYPE}"
                    _, args, kwargs = post.mock_calls[0]
                    self.assertEqual(args[0], f"{API_URL}/upload")
                    self.assertEqual(kwargs["files"]["file"].name, compressed_filename)
                    self.assertEqual(kwargs["files"]["readme"].name, os.path.join(self.path, README_FILE))
                    self.assertEqual(kwargs["data"], data)
                    self.assertEqual(kwargs["headers"], headers)