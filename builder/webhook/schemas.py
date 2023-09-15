from pydantic import BaseModel
from typing_extensions import Self
from webhook.client import WebhookClient


class SplightBaseSchema(BaseModel):
    def __hash__(self):  # make hashable BaseModel subclass
        return hash(self.__class__.__name__ + str(tuple(self.dict().values())))

    class Meta:
        partial = False


class APIObject(SplightBaseSchema):
    id: str

    @property
    def _webhook_client(self) -> WebhookClient[Self]:
        return WebhookClient[Self](schema=self.__class__)

    def save(self):
        self._webhook_client.update(state=self)

    class WebhookConfig:
        webhook_path: str
