import os
from unittest.mock import patch

import requests

from cli.component.component import Component
from cli.component.handler import ComponentHandler
from cli.tests.test_generic import SplightCLITest


class TestDelete(SplightCLITest):
    def setUp(self):
        super().setUp()
        self.original_component_path = self.path
        self.path = os.path.dirname(os.path.abspath(__file__))
        self.extracted_component_path = os.path.join(
            self.path, f"{self.name}-{self.version}"
        )
        self.component = Component(self.path, self.context)

    def test_component_delete(self):
        data = {
            "name": self.name,
            "version": self.version,
        }
        hub_url = self.context.workspace.settings.SPLIGHT_HUB_API_HOST
        component_type = self.type.lower()
        url = f"{hub_url}/{component_type}/remove/"
        with patch.object(
            ComponentHandler, "exists_in_hub", return_value=True
        ):
            response = requests.Response()
            response.status_code = 201
            with patch.object(requests, "post", return_value=response) as post:
                self.component.delete(self.name, self.type, self.version)
                _, args, kwargs = post.mock_calls[0]
                self.assertEqual(args[0], url)
                self.assertDictContainsSubset(kwargs["data"], data)
