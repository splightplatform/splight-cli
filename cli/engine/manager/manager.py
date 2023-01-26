from typing import Any, Dict, Type, List
import pandas as pd

from rich.console import Console
from rich.table import Table
from splight_abstract import AbstractDatabaseClient, AbstractDatalakeClient
from splight_models import SplightBaseModel
from datetime import datetime
from cli.utils import *
from cli.constants import DEFAULT_NAMESPACE

from cli.constants import warning_style

SplightModel = Type[SplightBaseModel]


class ResourceManagerException(Exception):
    pass


class DatalakeManagerException(Exception):
    pass


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
            for key, value in instance.dict().items() if key not in exclude_fields
        ]
        self._console.print(table)

    def list(self, skip: int = 0, limit: int = -1):
        instances = self._client.get(
            resource_type=self._model, skip_=skip, limit_=limit
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


class DatalakeManager:
    def __init__(
        self,
        client: AbstractDatalakeClient,
    ):
        self._client = client
        self._console = Console()

    # def __init__(self, context):
    #     self.context = context
    #     self.namespace = DEFAULT_NAMESPACE

    @property
    def sample_dataframe(self):
        return pd.read_csv(f"{BASE_DIR}/cli/datalake/dump_example.csv")

    def list(self):
        collections = self._client.list_collection_names()
        table = Table("", "Name")
        _ = [
            table.add_row(
                str(counter),
                collection,
            )
            for counter, collection in enumerate(collections)
        ]
        self._console.print(table)

    # def dump(self, collection, path, filter, example):
    #     if os.path.exists(path):
    #         raise Exception(f"File {path} already exists")
    #     if os.path.isdir(path):
    #         path = os.path.join(path, 'splight_dump.csv')
    #     elif not path.endswith(".csv"):
    #         raise Exception("Only CSV files are supported")

    #     if example:
    #         dataframe = self.sample_dataframe
    #     else:
    #         filters = {
    #             f.split('=')[0]: f.split('=')[1] for f in filter
    #         }

    #         dataframe = self.client.get_dataframe(
    #             resource_type=Variable,
    #             collection=collection,
    #             **self._get_filters()
    #         )
    #     dataframe.to_csv(path, index=False)
    #     click.secho(f"Succesfully dumpped {collection} in {path}", fg="green")

    # def load(self, collection, path, example):
    #     if not os.path.isfile(path):
    #         raise Exception("File not found")
    #     if not path.endswith(".csv"):
    #         raise Exception("Only CSV files are supported")

    #     if example:
    #         dataframe = self.sample_dataframe
    #     else:
    #         dataframe = pd.read_csv(path)
    #     self.client.save_dataframe(dataframe, collection=collection)
    #     click.secho(f"Succesfully loaded {path} in {collection}", fg="green")

    # @staticmethod
    # def _to_list(key: str, elem: str):
    #     if ',' not in elem and '__in' not in key:
    #         raise ValueError
    #     return list(elem.split(","))

    # @staticmethod
    # def _to_int(key: str, elem: str):
    #     if elem[0] == '-':
    #         can = elem[1:].isdigit()
    #     else:
    #         can = elem.isdigit()
    #     if not can:
    #         raise ValueError
    #     return int(elem)

    # @staticmethod
    # def _to_float(key: str, elem: str):
    #     try:
    #         return float(elem)
    #     except Exception:
    #         raise ValueError

    # @staticmethod
    # def _to_bool(key: str, elem: str):
    #     if elem == "True":
    #         return True
    #     elif elem == "False":
    #         return False
    #     else:
    #         raise ValueError

    # @staticmethod
    # def _to_date(key: str, elem: str):
    #     return datetime.strptime(elem, "%Y-%m-%dT%H:%M:%S%z")

    # def _get_filters(self, filters):
    #     to_cast = [
    #         self._to_list,
    #         self._to_int,
    #         self._to_float,
    #         self._to_bool,
    #         self._to_date
    #     ]
    #     parsed_filters = {}
    #     for key, value in filters.items():
    #         if key == 'limit_':
    #             parsed_filters[key] = value
    #             continue
    #         for cast in to_cast:
    #             try:
    #                 value = cast(key, value)
    #                 break
    #             except ValueError:
    #                 pass

    #         parsed_filters[key] = value
    #     return parsed_filters
