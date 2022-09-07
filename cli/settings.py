from pydantic import BaseSettings


class SplightCLISettings(BaseSettings):
    SPLIGHT_ACCESS_ID: str = None
    SPLIGHT_SECRET_KEY: str = None
    SPLIGHT_PLATFORM_API_HOST: str = 'https://api.splight-ai.com'
    # TODO REMOVE THIS
    SPLIGHT_HUB_API_HOST: str = 'https://hub.splight-ai.com'
    # FRAMEWORK
    DATABASE_CLIENT: str = "remote_splight_lib.database.DatabaseClient"
    DATALAKE_CLIENT: str = "remote_splight_lib.datalake.DatalakeClient"
    STORAGE_CLIENT: str = "remote_splight_lib.storage.StorageClient"
    DEPLOYMENT_CLIENT: str = "remote_splight_lib.deployment.DeploymentClient"


ALL_CONFIG_VARS = SplightCLISettings.__fields__
CONFIG_VARS = ["SPLIGHT_ACCESS_ID", "SPLIGHT_SECRET_KEY"]
