from typing import List, Type

from splight_abstract import AbstractDatabaseClient
from splight_models import SplightBaseModel

SplightModel = Type[SplightBaseModel]


class APIEndpoint:
    def __init__(
        self,
        client: AbstractDatabaseClient,
        model: SplightModel,
    ):
        self._client = client
        self._model = model

    def get(self, instance_id: str) -> SplightModel:
        instance = self._client.get(self._model, id=instance_id, first=True)
        return instance

    def list(self, skip: int = 0, limit: int = -1) -> List[SplightModel]:
        return self._client.get(self._model, skip_=skip, limit_=limit)

    def create(self, data):
        return

    def delete(self, instance_id: str):
        return instance_id
