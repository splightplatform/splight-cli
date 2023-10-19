from typing import List, Optional

from pydantic import BaseModel
from webhook.schemas import APIObject


class BuildSpec(BaseModel):
    id: str
    name: str
    version: str
    access_id: str
    secret_key: str
    cli_version: str
    api_host: str
    grpc_host: str


VERIFICATION_CHOICES = ["verified", "unverified", "official"]


class HubComponent(APIObject):
    id: Optional[str]
    name: str
    splight_cli_version: str
    build_status: Optional[str] = None
    description: Optional[str] = None
    privacy_policy: Optional[str] = None
    component_type: Optional[str] = None
    tenant: Optional[str] = None
    readme: Optional[str] = None
    picture: Optional[str] = None
    file: Optional[str] = None
    verification: Optional[str] = None
    created_at: Optional[str] = None
    last_modified: Optional[str] = None
    tags: List[str] = []
    min_component_capacity: Optional[str] = None
    usage_count: int = 0
    version: str

    class WebhookConfig:
        webhook_path = "v2/hub/component/webhook/"
