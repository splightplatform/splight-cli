from mock import patch
from cli.component.component import Component
from cli.component import push
from cli.context import FakeContext
from cli.utils.handler import ComponentHandler
from cli.tests.test_generic import SplightHubTest
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
        with patch.object(ComponentHandler, "exists_in_hub", return_value=False):
            result = self.runner.invoke(
                push,
                [self.type, self.path],
                obj=self.context
            )
        self.assertEqual(result.exit_code, 0)
        self.assertNotIn("Use \'splightcli configure\'\n", result.output)



    



