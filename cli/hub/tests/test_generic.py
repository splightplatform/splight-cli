import os
from unittest import TestCase
from cli.hub.settings import SPEC_FILE
from cli.context import Context
from cli.hub.utils import get_json_from_file

class SplightHubTest(TestCase):

    def setUp(self):
        self.path = os.path.join(os.path.dirname(__file__), "TestHub")
        self.component_json = get_json_from_file(os.path.join(self.path, SPEC_FILE))
        self.type = "algorithm"
        self.name = self.component_json['name']
        self.version = self.component_json['version']
        self.parameters = self.component_json['parameters']
        self.context = lambda : Context("default")