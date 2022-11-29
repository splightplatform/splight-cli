import json
import os
from unittest.mock import patch

import py7zr
import requests

from cli.component.component import Component, ComponentAlreadyExistsException
from cli.component.handler import ComponentHandler
from cli.constants import COMPRESSION_TYPE, README_FILE
from cli.tests.test_generic import SplightCLITest
from cli.settings import SPLIGHT_CLI_VERSION


class TestPush(SplightCLITest):
    def setUp(self):
        super().setUp()
        self.component = Component(self.path, self.context)

    @patch.object(ComponentHandler, "upload_component", return_value=None)
    @patch.object(ComponentHandler, "exists_in_hub", return_value=False)
    @patch.object(
        ComponentHandler,
        "get_component_info",
        return_value={"privacy_policy": "private"}
    )
    def test_push(self, retriever, exists_in_hub, uploader):
        self.component.push(force=False, public=False)
        exists_in_hub.assert_called_with(
            self.name, self.version
        )
        retriever.assert_called_with(
            self.name, self.version
        )
        uploader.assert_called_with(
            'private',
            self.name,
            self.version,
            self.tags,
            self.custom_types,
            self.input,
            self.output,
            self.commands,
            self.path,
        )

    def test_push_already_exists(self):
        with patch.object(
            ComponentHandler, "exists_in_hub", return_value=True
        ) as exists_in_hub:
            with patch.object(
                ComponentHandler, "upload_component"
            ) as uploader:
                with self.assertRaises(ComponentAlreadyExistsException):
                    self.component.push(force=False, public=False)
                exists_in_hub.assert_called_with(
                    self.name, self.version
                )
                uploader.assert_not_called()

    @patch.object(ComponentHandler, "upload_component", return_value=None)
    @patch.object(
        ComponentHandler,
        "get_component_info",
        return_value={"privacy_policy": "private"}
    )
    def test_push_forced(self, retriever, uploader):
        self.component.push(force=True, public=False)
        retriever.assert_called_with(
            self.name, self.version
        )
        uploader.assert_called_with(
            'private',
            self.name,
            self.version,
            self.tags,
            self.custom_types,
            self.input,
            self.output,
            self.commands,
            self.path,
        )

    @patch.object(ComponentHandler, "exists_in_hub", return_value=False)
    @patch.object(
        ComponentHandler,
        "get_component_info",
        return_value={"privacy_policy": "private"}
    )
    def test_component_upload(self, retriever, exists_in_hub):
        headers = {
            "Authorization": f"Splight {self.context.workspace.settings.SPLIGHT_ACCESS_ID} {self.context.workspace.settings.SPLIGHT_SECRET_KEY}"
        }
        data = {
            "name": self.name,
            "version": self.version,
            "privacy_policy": "private",
            "tags": self.tags,
            "custom_types": json.dumps(self.custom_types),
            "input": json.dumps(self.input),
            "output": json.dumps(self.output),
            "commands": json.dumps(self.commands),
            "splight_cli_version": SPLIGHT_CLI_VERSION,
        }

        response = requests.Response()
        response.status_code = 201
        with patch.object(requests, "post", return_value=response) as post:
            with patch.object(py7zr.SevenZipFile, "writeall") as writeall:
                self.component.push(force=False, public=False)
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
                    kwargs["data"], {**kwargs["data"], **data}
                )
                self.assertEqual(
                    kwargs["headers"], {**kwargs["headers"], **headers}
                )
