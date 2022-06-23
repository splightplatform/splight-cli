import os
import logging
from unittest import TestCase
from click.testing import CliRunner
from cli.settings import SPEC_FILE
from cli.context import Context 
from cli.utils import get_json_from_file
from cli.workspace import create, delete, select


logger = logging.getLogger()
logger.setLevel(logging.WARNING)

class SplightHubTest(TestCase):

    def setUp(self):
        self.path = os.path.join(os.path.dirname(__file__), "TestHub")
        self.component_json = get_json_from_file(os.path.join(self.path, SPEC_FILE))
        self.type = "algorithm"
        self.name = self.component_json['name']
        self.version = self.component_json['version']
        self.parameters = self.component_json['parameters']
        self.privacy_policy = "private"
        self.access_id = "access_id"
        self.secret_key = "secret_key"
        self.hub_api_host = "https://integrationhub.splight-ae.com"
        self.context = Context()
        self.runner = CliRunner()
        

    def tearDown(self) -> None:
        return super().tearDown()
