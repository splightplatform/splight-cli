import os
import requests
from unittest.mock import patch
from cli.component.component import Component
from cli.utils import ComponentHandler
from cli.tests.test_generic import SplightHubTest
from cli.settings import *

class TestPull(SplightHubTest):

    def setUp(self):
        super().setUp()
        self.original_component_path = self.path
        self.path = os.path.dirname(os.path.abspath(__file__))
        self.extracted_component_path = os.path.join(self.path, f"{self.name}-{self.version}")
        self.component = Component(self.path, self.context)

    def test_component_delete(self):
        headers = {
            'Authorization': f"Splight {self.context.SPLIGHT_ACCESS_ID} {self.context.SPLIGHT_SECRET_KEY}"
        }
        data = {
            'name': self.name,
            'version': self.version,
        }

        with patch.object(ComponentHandler, "exists_in_hub", return_value=True):
            response = requests.Response()
            response.status_code = 201
            with patch.object(requests, "post", return_value=response) as post:
                    self.component.delete(self.name, self.type, self.version)
                    _, args, kwargs = post.mock_calls[0]
                    self.assertEqual(args[0], f"{self.context.SPLIGHT_HUB_API_HOST}/{self.type}/remove/")
                    self.assertDictContainsSubset(kwargs["data"], data)
                
