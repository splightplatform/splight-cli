import os
from unittest import TestCase
from cli.settings import SPEC_FILE
from cli.context import Context, CONFIG_FILE 
from cli.utils import get_json_from_file

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
        self.hub_api_host = "https://fakehub.splight-ae.com"
        with open(CONFIG_FILE, "w") as f:
            f.write(f"SPLIGHT_ACCESS_ID={self.access_id}\nSPLIGHT_SECRET_KEY={self.secret_key}\nSPLIGHT_HUB_API_HOST={self.hub_api_host}")
        self.context = Context()
