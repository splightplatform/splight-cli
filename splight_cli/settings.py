from typing import Dict

from pydantic import BaseModel, ConfigDict
from pydantic_settings import BaseSettings

from splight_cli.version import __version__


class SplightCLISettings(BaseSettings):
    SPLIGHT_ACCESS_ID: str = ""
    SPLIGHT_SECRET_KEY: str = ""
    SPLIGHT_PLATFORM_API_HOST: str = "https://api.splight-ai.com"
    SPLIGHT_GRPC_HOST: str = "grpc.splight-ai.com:443"

    model_config: ConfigDict = ConfigDict(extra="ignore")


class SplightCLIConfig(BaseModel):
    current_workspace: str
    workspaces: Dict[str, SplightCLISettings]


ALL_CONFIG_VARS = set(SplightCLISettings.model_fields.keys())
CONFIG_VARS = [
    "SPLIGHT_ACCESS_ID",
    "SPLIGHT_SECRET_KEY",
]
SPLIGHT_CLI_VERSION = __version__
