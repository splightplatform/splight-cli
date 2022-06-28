import os
import logging
from unittest import TestCase
from click.testing import CliRunner
from cli.settings import SPEC_FILE
from cli.context import FakeContext, PrivacyPolicy 
from cli.utils import get_json_from_file


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
        self.privacy_policy = PrivacyPolicy.PRIVATE
        self.context = FakeContext(privacy_policy=self.privacy_policy)
        self.runner = CliRunner()
    
    def set_fake_credentials(self):
        self.credentials = {
            "SPLIGHT_ACCESS_ID": "access_id",
            "SPLIGHT_SECRET_KEY": "secret_key"
        }
        self.context.set(**self.credentials)

    def tearDown(self) -> None:
        return super().tearDown()
