from typing import Generic, Type, TypeVar

from furl import furl
from pydantic import BaseModel, BaseSettings
from requests import Response
from webhook.auth import HmacSignature

T = TypeVar("T", bound=BaseModel)
K = TypeVar("K")


def get_signature(payload: bytes, secret: str) -> str:
    hmac = HmacSignature(secret=secret)
    signature = hmac.compute_header_signature(payload)
    return signature


def validate_signature(payload: bytes, signature: str, secret: str) -> bool:
    return HmacSignature.verify_header(payload, signature, secret)


class InvalidSchema(Exception):
    ...


class WebhookClientSettings(BaseSettings):
    SPLIGHTD_WEBHOOK_SECRET: str
    SPLIGHT_API_HOST: str


class WebhookClient(Generic[T]):
    settings = WebhookClientSettings()
    SECRET = settings.SPLIGHTD_WEBHOOK_SECRET
    API_HOST = furl(settings.SPLIGHT_API_HOST)

    def __init__(self, schema: Type[T]) -> None:
        if schema.Meta.partial:
            raise InvalidSchema("Partial schemas are not supported")
        self._schema = schema
        self._resource_path = schema.WebhookConfig.webhook_path

    def _validated_instance(self, response: Response) -> T:
        response.raise_for_status()
        return self._schema.parse_raw(response.json())

    def update(self, instance: T, pk: str) -> T:
        payload = instance.json(exclude_unset=instance.Meta.partial).encode(
            "utf-8"
        )
        signature = get_signature(payload, self.SECRET)
        headers = {
            "Content-Type": "application/json",
            "Splight-Signature": signature,
        }

        response = requests.request(
            method="PATCH" if instance.Meta.partial else "PUT",
            url=self.API_HOST / self._resource_path / f"{pk}/",
            data=payload,
            headers=headers,
        )
        return self._validated_instance(response)

    def retrieve(self, pk: str) -> T:
        response = requests.get(self.API_HOST / self._resource_path / f"{pk}/")
        return self._validated_instance(response)
