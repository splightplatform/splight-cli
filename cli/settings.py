import uuid
from typing import Optional

from pydantic import BaseSettings, Extra, Field


class SplightCLISettings(BaseSettings):
    SPLIGHT_ACCESS_ID: str = None
    SPLIGHT_SECRET_KEY: str = None
    SPLIGHT_PLATFORM_API_HOST: str = "https://api.splight-ai.com"
    # FRAMEWORK
    DATABASE_CLIENT: str = "remote_splight_lib.database.DatabaseClient"
    DATALAKE_CLIENT: str = "remote_splight_lib.datalake.DatalakeClient"
    STORAGE_CLIENT: str = "remote_splight_lib.storage.StorageClient"
    DEPLOYMENT_CLIENT: str = "remote_splight_lib.deployment.DeploymentClient"
    COMMUNICATION_CLIENT: str = (
        "remote_splight_lib.communication.CommunicationClient"
    )
    COMPONENT_ID: Optional[str] = Field(default=str(uuid.uuid4()))

    class Config:
        extra = Extra.ignore


ALL_CONFIG_VARS = SplightCLISettings.__fields__
CONFIG_VARS = [
    "SPLIGHT_ACCESS_ID",
    "SPLIGHT_SECRET_KEY",
    "COMPONENT_ID",
]
