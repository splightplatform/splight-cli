from typing import Dict

from cli.version import __version__
from pydantic import BaseModel, BaseSettings, Extra


class SplightCLISettings(BaseSettings):
    SPLIGHT_ACCESS_ID: str = ""
    SPLIGHT_SECRET_KEY: str = ""
    SPLIGHT_PLATFORM_API_HOST: str = "https://api.splight-ai.com"
    # FRAMEWORK
    DATABASE_CLIENT: str = "splight_lib.client.database.RemoteDatabaseClient"
    DATALAKE_CLIENT: str = "splight_lib.client.datalake.RemoteDatalakeClient"
    HUB_CLIENT: str = "splight_lib.client.hub.SplightHubClient"
    COMMUNICATION_CLIENT: str = (
        "splight_lib.client.communication.RemoteCommunicationClient"
    )
    NAMESPACE: str = "NO_NAMESPACE"

    class Config:
        extra = Extra.ignore


class SplightCLIConfig(BaseModel):
    current_workspace: str
    workspaces: Dict[str, SplightCLISettings]


ALL_CONFIG_VARS = SplightCLISettings.__fields__
CONFIG_VARS = [
    "SPLIGHT_ACCESS_ID",
    "SPLIGHT_SECRET_KEY",
]
SPLIGHT_CLI_VERSION = __version__
