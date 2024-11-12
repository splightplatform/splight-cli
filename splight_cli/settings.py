from typing import Dict

from pydantic import BaseModel, ConfigDict
from pydantic_settings import BaseSettings

from splight_cli.version import __version__


class SplightCLISettings(BaseSettings):
    SPLIGHT_ACCESS_ID: str | None = None
    SPLIGHT_SECRET_KEY: str | None = None
    SPLIGHT_PLATFORM_API_HOST: str = "https://api.splight-ai.com"

    model_config: ConfigDict = ConfigDict(extra="ignore")

    def is_configured(self) -> bool:
        return (
            False
            if not self.SPLIGHT_ACCESS_ID or not self.SPLIGHT_SECRET_KEY
            else True
        )


class SplightCLIConfig(BaseModel):
    current_workspace: str = "default"
    workspaces: Dict[str, SplightCLISettings]


ALL_CONFIG_VARS = set(SplightCLISettings.model_fields.keys())
CONFIG_VARS = [
    "SPLIGHT_ACCESS_ID",
    "SPLIGHT_SECRET_KEY",
]
SPLIGHT_CLI_VERSION = __version__
