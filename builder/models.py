from typing import List, Optional

from pydantic import BaseModel


class BuildSpec(BaseModel):
    name: str
    version: str
    access_id: str
    secret_key: str
    cli_version: str
    api_host: str
    grpc_host: str


VERIFICATION_CHOICES = ["verified", "unverified", "official"]


class HubComponent(BaseModel):
    id: Optional[str]
    name: str
    splight_cli_version: str
    build_status: Optional[str]
    description: Optional[str]
    privacy_policy: Optional[str] = None
    component_type: Optional[str] = None
    tenant: Optional[str] = None
    readme: Optional[str]
    picture: Optional[str]
    file: Optional[str]
    verification: Optional[str]
    created_at: Optional[str]
    last_modified: Optional[str]
    tags: List[str] = []
    min_component_capacity: Optional[str]
    usage_count: int = 0
    version: str
