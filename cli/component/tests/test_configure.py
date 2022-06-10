import os
import subprocess
from cli.component.component import Component
from cli.cli import configure
from cli.context import CONFIG_FILE
from .test_generic import SplightHubTest
from ...settings import *

class TestPush(SplightHubTest):

    def setUp(self):
        super().setUp()
        self.component = Component(self.path, self.context)
        self.current_dir = os.path.dirname(__file__)
        os.remove(CONFIG_FILE)

    def test_no_configuration(self):
        self.component = Component(self.path, self.context)
        output = None
        try:
            output = subprocess.check_output("splightcli component push algorithm TestHub", shell=True, cwd=self.current_dir)
        except subprocess.CalledProcessError as e:
            output = e.output
        self.assertEqual(output, b"Please set your Splight credentials. Use \"splighthub configure\"\n")




    



