import requests
import json
from mock import patch
from cli.component.component import Component
from cli.component import push
from cli.context import Context, FakeContext
from cli.utils.handler import ComponentHandler
from .test_generic import SplightHubTest
from ...settings import *


class TestConfigure(SplightHubTest):

    def test_configure_requested(self):
        self.component = Component(self.path, self.context)
        self.context = FakeContext()
        result = self.runner.invoke(
            push,
            [self.type, self.path],
            obj=self.context
        )
        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("Please set your Splight credentials. Use \"splightcli configure\"\n", result.output)

    def test_configure_not_requested(self):
        self.component = Component(self.path, self.context)
        self.context = FakeContext()
        self.set_fake_credentials()
        response = requests.Response()
        response.status_code = 201
        with patch.object(ComponentHandler, "exists_in_hub", return_value=False):
            with patch('requests.post', return_value=response) as post:
                result = self.runner.invoke(
                    push,
                    [self.type, self.path],
                    obj=self.context
                )
        self.assertEqual(result.exit_code, 0)
        self.assertNotIn("Use \'splightcli configure\'\n", result.output)
        self.assertIn("Component pushed successfully to Splight Hub", result.output)



    



