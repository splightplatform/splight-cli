import os
import click
from enum import Enum
from .config import ConfigManager

SPLIGHT_PATH = os.path.join(os.path.expanduser("~"), '.splight')
CONFIG_FILE = os.path.join(SPLIGHT_PATH, 'hub.conf')
class PrivacyPolicy(Enum):
    PUBLIC = "public"
    PRIVATE = "private"

class Context:
    privacy_policy = None

    def __init__(self):
        self.privacy_policy = PrivacyPolicy.PRIVATE
        try:
            with open(CONFIG_FILE, 'r') as file:
                config_manager = ConfigManager(file)
                config = config_manager.load_config()
                self.SPLIGHT_ACCESS_ID, self.SPLIGHT_SECRET_KEY = config.get('SPLIGHT_ACCESS_ID'), config.get('SPLIGHT_SECRET_KEY')
        except FileNotFoundError:
            if not os.path.exists(SPLIGHT_PATH):
                os.makedirs(SPLIGHT_PATH)
            open(CONFIG_FILE, 'a').close()
            self.SPLIGHT_ACCESS_ID, self.SPLIGHT_SECRET_KEY = None, None

    def __repr__(self):
        return f"<Context>"


pass_context = click.make_pass_decorator(Context)