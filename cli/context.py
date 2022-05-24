import os
import click
from enum import Enum
from .config import ConfigManager

SPLIGHT_PATH = os.path.join(os.path.expanduser("~"), '.splight')
CONFIG_FILE = os.path.join(SPLIGHT_PATH, 'hub.conf')

HUB_CONFIGS = [
    "SPLIGHT_ACCESS_ID",
    "SPLIGHT_SECRET_KEY",
    "SPLIGHT_HUB_API_HOST",
]

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
                for config_key in HUB_CONFIGS:
                    setattr(self, config_key, config.get(config_key))
        except FileNotFoundError:
            if not os.path.exists(SPLIGHT_PATH):
                os.makedirs(SPLIGHT_PATH)
            open(CONFIG_FILE, 'a').close()
            for config_key in HUB_CONFIGS:
                setattr(self, config_key, None)

    def __repr__(self):
        return f"<Context>"


pass_context = click.make_pass_decorator(Context)