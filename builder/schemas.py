from pydantic import BaseModel


class BuildSpec(BaseModel):
    id: str
    name: str
    version: str
    access_id: str
    secret_key: str
    cli_version: str
    api_host: str
    grpc_host: str
