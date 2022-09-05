from pydantic import BaseSettings


class SplightCLISettings(BaseSettings):
    SPLIGHT_ACCESS_ID: str = None
    SPLIGHT_SECRET_KEY: str = None
    SPLIGHT_PLATFORM_API_HOST: str = 'https://integrationapi.splight-ae.com'
    # TODO REMOVE THIS
    SPLIGHT_HUB_API_HOST: str = 'https://integrationhub.splight-ae.com'
    # FRAMEWORK
    DATABASE_CLIENT: str = 'private_splight_lib.database.DjangoClient'
    DATALAKE_CLIENT: str = "private_splight_lib.datalake.MongoClient"
    STORAGE_CLIENT: str = "remote_splight_lib.storage.StorageClient"
    DEPLOYMENT_CLIENT: str = "remote_splight_lib.deployment.DeploymentClient"


ALL_CONFIG_VARS = SplightCLISettings.__fields__
CONFIG_VARS = ["SPLIGHT_ACCESS_ID", "SPLIGHT_SECRET_KEY"]
