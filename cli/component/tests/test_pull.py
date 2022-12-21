import os
import shutil
from unittest.mock import patch

import requests

from cli.component.component import Component
from cli.component.handler import ComponentHandler
from cli.constants import COMPRESSION_TYPE
from cli.tests.test_generic import SplightCLITest


class TestPull(SplightCLITest):
    def setUp(self):
        super().setUp()
        self.original_component_path = self.path
        self.path = os.path.dirname(os.path.abspath(__file__))
        self.extracted_component_path = os.path.join(
            self.path, f"{self.name}-{self.version}"
        )
        self.component = Component(self.path, self.context)

    def test_pull(self):
        with patch.object(
            ComponentHandler, "download_component"
        ) as downloader:
            self.component.pull(self.name, self.version)
            downloader.assert_called_with(
                self.name, self.version, self.path
            )

    def test_pull_already_exists_in_local(self):
        already_component = os.path.join(
            self.path, f"{self.name}-{self.version}"
        )
        os.mkdir(already_component)
        with self.assertRaises(Exception):
            self.component.pull(self.name, self.version)
        shutil.rmtree(already_component)

    def test_component_download(self):
        try:
            headers = {
                "Authorization": f"Splight {self.context.workspace.settings.SPLIGHT_ACCESS_ID} {self.context.workspace.settings.SPLIGHT_SECRET_KEY}"
            }
            data = {
                "name": self.name,
                "version": self.version,
            }
            with patch.object(
                ComponentHandler, "exists_in_hub", return_value=True
            ):
                compressed_filename = (
                    f"{self.name}-{self.version}.{COMPRESSION_TYPE}"
                )
                file = None
                with open(
                    os.path.join(
                        self.original_component_path, compressed_filename
                    ),
                    "rb",
                ) as f:
                    file = f.read()
                response = requests.Response()
                response.status_code = 200
                response._content = file
                with patch.object(
                    requests, "post", return_value=response
                ) as post:
                    os.chdir(self.path)
                    self.component.pull(self.name, self.version)
                    _, args, kwargs = post.mock_calls[0]
                    self.assertEqual(
                        args[0],
                        f"{self.context.workspace.settings.SPLIGHT_PLATFORM_API_HOST}/hub/download/",
                    )
                    self.assertEqual(
                        kwargs["data"], {**kwargs["data"], **data}
                    )
                    self.assertEqual(
                        kwargs["headers"], {**kwargs["headers"], **headers}
                    )

                    self.assertTrue(
                        os.path.exists(self.extracted_component_path)
                    )
        finally:
            if os.path.exists(self.extracted_component_path):
                shutil.rmtree(self.extracted_component_path)
