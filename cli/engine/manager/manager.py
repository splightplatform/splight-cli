import os
from datetime import datetime
from typing import Any, Dict, List, Optional, Type, Union

import pandas as pd
from pydantic import BaseModel
from rich.console import Console
from rich.table import Table
from splight_abstract import AbstractDatabaseClient, AbstractDatalakeClient
from splight_models import Component, DatalakeModel, SplightBaseModel

from cli.constants import success_style, warning_style

SplightModel = Type[SplightBaseModel]


class ResourceManagerException(Exception):
    pass


class DatalakeManagerException(Exception):
    pass


class QueryParam(BaseModel):
    value: Union[List[int], List[float], List[str], int, float, str]


class ResourceManager:
    def __init__(
        self,
        client: AbstractDatabaseClient,
        model: SplightModel,
    ):
        self._client = client
        self._model = model
        self._resource_name = model.__name__
        self._console = Console()

    def get(self, instance_id: str, exclude_fields: List[str] = None):
        exclude_fields = exclude_fields if exclude_fields is not None else []
        instance = self._client.get(self._model, id=instance_id, first=True)
        if not instance:
            raise ResourceManagerException(
                f"No {self._resources_name} found with ID = {instance_id}",
                style=warning_style,
            )

        name = instance.name if hasattr(instance, "name") else instance.title
        table = Table(
            title=f"{self._resource_name} = {name}", show_header=False
        )
        _ = [
            table.add_row(key, str(value))
            for key, value in instance.dict().items()
            if key not in exclude_fields
        ]
        self._console.print(table)

    def list(self, params: Dict[str, Any]):
        instances = self._client.get(
            resource_type=self._model,
            **params,
        )
        table = Table("", "ID", "Name")
        _ = [
            table.add_row(
                str(counter),
                item.id,
                item.name if hasattr(item, "name") else item.title,
            )
            for counter, item in enumerate(instances)
        ]
        self._console.print(table)

    def create(self, data: Dict[str, Any]):
        instance = self._client.save(instance=self._model.parse_obj(data))
        table = Table(
            title=f"{self._resource_name} = {instance.name}", show_header=False
        )
        _ = [
            table.add_row(key, str(value))
            for key, value in instance.dict().items()
        ]
        self._console.print(table)

    def delete(self, instance_id: str):
        self._client.delete(resource_type=self._model, id=instance_id)
        self._console.print(
            f"{self._resource_name}={instance_id} deleted", style=warning_style
        )

    def download(self, instance_id: str, path: str):
        instance = self._client.get(self._model, id=instance_id, first=True)
        download = self._client.download(instance, decrypt=False)
        if not instance:
            raise ResourceManagerException(
                f"No {self._resources_name} found with ID = {instance_id}",
                style=warning_style,
            )
        if not path:
            path = instance.file
        with open(path, "wb+") as file:
            file.write(download.read())
        self._console.print(
            f"{self._resource_name}={instance_id} downloaded to {path}",
            style=warning_style,
        )

    @staticmethod
    def get_query_params(filters: Optional[List[str]]) -> Dict[str, Any]:
        params = {}
        filter_dict = {}
        for filter in filters:
            key, v = filter.split("=")
            if "__in" in key:
                value = filter_dict.get(key, [])
                value.append(v)
                filter_dict[key] = value
            else:
                filter_dict[key] = v

        params = {
            key: QueryParam(value=value).value
            for key, value in filter_dict.items()
        }
        return params


class DatalakeManager:
    def __init__(
        self,
        db_client: AbstractDatabaseClient,
        dl_client: AbstractDatalakeClient,
    ):
        self._db_client = db_client
        self._dl_client = dl_client
        self._console = Console()

    def list(self, skip, limit):
        instances = [{"id": "default", "name": "-"}]
        components = self._db_client.get(resource_type=Component)
        components = [component.dict() for component in components]
        instances.extend(components)
        instances = instances[
            skip : (limit + skip if limit is not None else None)
        ]
        table = Table("", "Name", "Component reference")
        _ = [
            table.add_row(
                str(counter),
                item.get("id"),
                item.get("name"),
            )
            for counter, item in enumerate(instances)
        ]
        self._console.print(table)

    def dump(self, collection, path, filters):
        if os.path.exists(path):
            raise Exception(f"File {path} already exists")
        if os.path.isdir(path):
            path = os.path.join(path, "splight_dump.csv")
        elif not path.endswith(".csv"):
            raise Exception("Only CSV files are supported")

        DatalakeModel.Meta.collection_name = collection
        dataframe = self._dl_client.get_dataframe(
            resource_type=DatalakeModel, **self._get_filters(filters)
        )
        dataframe.to_csv(path)
        self._console.print(
            f"Succesfully dumpped {collection} in {path}",
            style=success_style,
        )

    def load(self, collection, path):
        if not os.path.isfile(path):
            raise Exception("File not found")
        if not path.endswith(".csv"):
            raise Exception("Only CSV files are supported")

        dataframe = pd.read_csv(path)
        dataframe = dataframe.set_index("timestamp")
        DatalakeModel.Meta.collection_name = collection
        self._dl_client.save_dataframe(DatalakeModel, dataframe)
        self._console.print(
            f"Succesfully loaded {path} in {collection}",
            style=success_style,
        )

    @staticmethod
    def _to_list(key: str, elem: str):
        if "," not in elem and "__in" not in key:
            raise ValueError
        return list(elem.split(","))

    @staticmethod
    def _to_int(key: str, elem: str):
        if elem[0] == "-":
            can = elem[1:].isdigit()
        else:
            can = elem.isdigit()
        if not can:
            raise ValueError
        return int(elem)

    @staticmethod
    def _to_float(key: str, elem: str):
        try:
            return float(elem)
        except Exception:
            raise ValueError

    @staticmethod
    def _to_bool(key: str, elem: str):
        if elem == "True":
            return True
        elif elem == "False":
            return False
        else:
            raise ValueError

    @staticmethod
    def _to_date(key: str, elem: str):
        return datetime.strptime(elem, "%Y-%m-%dT%H:%M:%S%z")

    def _get_filters(self, filters):
        to_cast = [
            self._to_list,
            self._to_int,
            self._to_float,
            self._to_bool,
            self._to_date,
        ]
        parsed_filters = {}
        for key, value in filters.items():
            if key == "limit_":
                parsed_filters[key] = value
                continue
            for cast in to_cast:
                try:
                    value = cast(key, value)
                    break
                except ValueError:
                    pass

            parsed_filters[key] = value
        return parsed_filters
