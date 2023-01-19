import json
import os
from unittest.mock import patch

import py7zr
import requests

from cli.component.component import Component, ComponentAlreadyExistsException
from cli.component.handler import ComponentHandler
from cli.constants import COMPRESSION_TYPE, README_FILE
from cli.tests.test_generic import SplightCLITest


class TestPush(SplightCLITest):
    def setUp(self):
        super().setUp()
        self.component = Component(self.context)

    @patch.object(ComponentHandler, "upload_component", return_value=None)
    @patch.object(ComponentHandler, "exists_in_hub", return_value=False)
    def test_push(self, exists_in_hub, uploader):
        self.component.push(self.path, force=False)
        exists_in_hub.assert_called_with(self.name, self.version)
        uploader.assert_called_with(self.spec, local_path=self.path)

    @patch.object(ComponentHandler, "upload_component", return_value=None)
    @patch.object(ComponentHandler, "exists_in_hub", return_value=True)
    def test_push_already_exists(self, exists_in_hub, uploader):
        with self.assertRaises(ComponentAlreadyExistsException):
            self.component.push(self.path, force=False)
        exists_in_hub.assert_called_with(self.name, self.version)
        uploader.assert_not_called()

    @patch.object(ComponentHandler, "upload_component", return_value=None)
    @patch.object(ComponentHandler, "exists_in_hub", return_value=True)
    def test_push_forced(self, exists_in_hub, uploader):
        self.component.push(path=self.path, force=True)
        uploader.assert_called_with(self.spec, local_path=self.path)

    @patch.object(ComponentHandler, "exists_in_hub", return_value=False)
    def test_component_upload(self, exists_in_hub):
        self.maxDiff = None
        headers = {
            "Authorization": f"Splight {self.context.workspace.settings.SPLIGHT_ACCESS_ID} {self.context.workspace.settings.SPLIGHT_SECRET_KEY}"
        }
        data = {
            'name': self.spec.name,
            'version': self.spec.version,
            'splight_cli_version': self.spec.splight_cli_version,
            'privacy_policy': self.spec.privacy_policy,
            'tags': self.spec.tags,
            'custom_types': json.dumps([x.dict() for x in self.spec.custom_types]),
            'input': json.dumps([x.dict() for x in self.spec.input]),
            'output': json.dumps([x.dict() for x in self.spec.output]),
            'commands': json.dumps([x.dict() for x in self.spec.commands]),
            'bindings': json.dumps([x.dict() for x in self.spec.bindings]),
            'endpoints': json.dumps([x.dict() for x in self.spec.endpoints]),
        }

        response = requests.Response()
        response.status_code = 201
        with patch.object(requests, "post", return_value=response) as post:
            with patch.object(py7zr.SevenZipFile, "writeall") as writeall:
                self.component.push(self.path, force=False)
                writeall.assert_called_with(
                    self.path, f"{self.name}-{self.version}"
                )
                compressed_filename = (
                    f"{self.name}-{self.version}.{COMPRESSION_TYPE}"
                )
                _, args, kwargs = post.mock_calls[0]
                self.assertEqual(
                    args[0],
                    f"{self.context.workspace.settings.SPLIGHT_PLATFORM_API_HOST}/hub/upload/",
                )
                self.assertEqual(
                    kwargs["files"]["file"].name, compressed_filename
                )
                self.assertEqual(
                    kwargs["files"]["readme"].name,
                    os.path.join(self.path, README_FILE),
                )
                self.assertEqual(
                    kwargs["headers"], {**kwargs["headers"], **headers}
                )
                self.assertEqual(
                    kwargs["data"], data
                )
