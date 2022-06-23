import os
from cli.component.component import Component
from cli.component import push
from cli.context import Context, FakeContext
from .test_generic import SplightHubTest
from ...settings import *

class TestPush(SplightHubTest):

    def test_no_configuration(self):
        self.component = Component(self.path, self.context)
        self.context = FakeContext()
        result = self.runner.invoke(
            push,
            [self.type, self.path],
            input="asd", # WHY?
            obj=self.context
        )
        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("Please set your Splight credentials. Use \"splightcli configure\"\n", result.output)




    



