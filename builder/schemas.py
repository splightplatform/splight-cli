from pydantic import BaseModel


class BuildSpec(BaseModel):
    id: str
    name: str
    version: str
    cli_version: str
