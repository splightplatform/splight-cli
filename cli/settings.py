from typing import Dict

from pydantic import BaseModel, BaseSettings, Extra

from cli.version import __version__


class SplightCLISettings(BaseSettings):
    SPLIGHT_ACCESS_ID: str = ""
    SPLIGHT_SECRET_KEY: str = ""
    SPLIGHT_PLATFORM_API_HOST: str = "https://api.splight-ai.com"
    # FRAMEWORK
    DATABASE_CLIENT: str = "remote_splight_lib.database.DatabaseClient"
    DATALAKE_CLIENT: str = "remote_splight_lib.datalake.DatalakeClient"
    HUB_CLIENT: str = "remote_splight_lib.hub.SplightHubClient"
    STORAGE_CLIENT: str = "remote_splight_lib.storage.StorageClient"
    BLOCKCHAIN_CLIENT: str = "remote_splight_lib.blockchain.BlockchainClient"
    DEPLOYMENT_CLIENT: str = "remote_splight_lib.deployment.DeploymentClient"
    COMMUNICATION_CLIENT: str = (
        "remote_splight_lib.communication.CommunicationClient"
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
