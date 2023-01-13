from typing import Dict, List, Optional, Type

import requests
from furl import furl
from splight_models import SplightBaseModel


class APIEndpoint:
    def __init__(
        self,
        url: str,
        path: str,
        model: Type[SplightBaseModel],
        headers: Optional[Dict[str, str]] = None,
    ):
        self._base_url = furl(url)
        self._path = path if path.endswith("/") else f"{path}/"
        self._session = requests.Session()
        self._model = model
        if headers:
            self._session.headers.update(headers)

    def get(self, instance_id: str) -> Type[SplightBaseModel]:
        url = self._base_url / self._path / f"{instance_id}/"
        response = self._session.get(url)
        response.raise_for_status()
        return self._model.parse_obj(response.json())

    def list(self) -> List:
        url = self._base_url / self._path
        instances = []
        for new_instances in self._list(url):
            instances.extend(
                [self._model.parse_obj(item) for item in new_instances]
            )
        return instances

    def create(self, data):
        return

    def delete(self, instance_id: str):
        return instance_id

    def _list(self, url: furl):
        page_url = str(url)

        while page_url:
            response = self._session.get(page_url)
            response.raise_for_status()
            data = response.json()
            if data["next"]:
                page_url = data["next"]
            else:
                page_url = None

            yield data["results"]
