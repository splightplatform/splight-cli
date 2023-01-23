from typing import Any, Dict, Type

from rich.console import Console
from rich.table import Table
from splight_abstract import AbstractDatabaseClient
from splight_models import SplightBaseModel

from cli.constants import warning_style

SplightModel = Type[SplightBaseModel]


class ResourceManagerException(Exception):
    pass


class ResourceManager:
    def __init__(
        self,
        client: AbstractDatabaseClient,
        model: SplightModel,
    ):
        self._client = client
        self._model = model
        self._console = Console()

    def get(self, instance_id: str):
        instance = self._client.get(self._model, id=instance_id, first=True)
        if not instance:
            raise ResourceManagerException(
                f"No Asset found with ID = {instance_id}", style=warning_style
            )
        table = Table(title=f"Asset = {instance.name}", show_header=False)
        _ = [
            table.add_row(key, str(value))
            for key, value in instance.dict().items()
        ]
        self._console.print(table)

    def list(self, skip: int = 0, limit: int = -1):
        instances = self._client.get(
            resource_type=self._model, skip_=skip, limit_=limit
        )
        table = Table("", "ID", "Name")
        _ = [
            table.add_row(str(counter), item.id, item.name)
            for counter, item in enumerate(instances)
        ]
        self._console.print(table)

    def create(self, data: Dict[str, Any]):
        instance = self._client.save(instance=self._model.parse_obj(data))
        resource = self._model.__name__
        table = Table(title=f"{resource} = {instance.name}", show_header=False)
        _ = [
            table.add_row(key, str(value))
            for key, value in instance.dict().items()
        ]
        self._console.print(table)

    def delete(self, instance_id: str):
        self._client.delete(resource_type=self._model, id=instance_id)
        resource = self._model.__name__
        self._console.print(
            f"{resource}={instance_id} deleted", style=warning_style
        )
