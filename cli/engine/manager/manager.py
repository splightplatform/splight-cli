import os
from datetime import datetime
from typing import Any, Dict, List, Optional, Type, Union

import pandas as pd
import requests
import typer
from pydantic import BaseModel
from rich.console import Console
from rich.table import Table
from splight_abstract import AbstractDatabaseClient, AbstractDatalakeClient
from splight_models import (
    Component,
    ComponentObject,
    DatalakeModel,
    HubComponent,
    InputParameter,
    Parameter,
    SplightBaseModel,
)

from cli.component.exceptions import InvalidCSVColumns
from cli.component.loaders import SpecLoader
from cli.constants import REQUIRED_DATALAKE_COLUMNS  # error_style,
from cli.constants import success_style, warning_style
from cli.engine.manager.exceptions import (
    ComponentCreateError,
    InvalidComponentId,
    UpdateParametersError,
    VersionUpdateError,
)
from cli.hub.component.exceptions import HubComponentNotFound
from cli.hub.component.hub_manager import HubComponentManager

SplightModel = Type[SplightBaseModel]


class ResourceManagerException(Exception):
    pass


class DatalakeManagerException(Exception):
    pass


class ComponentUpgradeManagerException(Exception):
    def __init__(self, message=None):
        self.message = message

    def __str__(self):
        return self.message


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
                item.name
                if hasattr(item, "name")
                else getattr(item, "title", ""),
            )
            for counter, item in enumerate(instances)
        ]
        self._console.print(table)

    def create(self, data: Dict[str, Any]):
        instance = self._client.save(instance=self._model.parse_obj(data))
        table = Table(
            title=f"{self._resource_name} = {getattr(instance,'name', '')}",
            show_header=False,
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
            skip: (limit + skip if limit is not None else None)  # fmt: skip
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

    def load(self, collection: str, path: str):
        if not os.path.isfile(path):
            raise Exception("File not found")
        if not path.endswith(".csv"):
            raise Exception("Only CSV files are supported")

        dataframe = pd.read_csv(path)
        self._validate_csv(dataframe)
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

    def _validate_csv(self, data: pd.DataFrame):
        required_columns = REQUIRED_DATALAKE_COLUMNS

        if not required_columns.issubset(set(data.columns)):
            raise InvalidCSVColumns(columns=required_columns)


class ComponentUpgradeManager:
    def __init__(self, context: typer.Context, component_id: str):
        self.db_client = context.obj.framework.setup.DATABASE_CLIENT()
        self.hubmanager = HubComponentManager(
            client=context.obj.framework.setup.HUB_CLIENT()
        )
        self.component_id = component_id
        self._console = Console()

    def _create_objects(
        self,
        previous: List[InputParameter],
        hub: List[Parameter],
        debug: bool = False,
    ):
        prev_parameters, hub_parameters, result = self._update_parameters(
            previous, hub
        )
        step = 2
        if debug:
            self._console.print(
                "Updating parameters, we will ask for missing required"
                " parameters if needed."
            )
        for param in hub_parameters.keys():
            if param not in prev_parameters.keys():
                parameter = hub_parameters[param]
                try:
                    if parameter["required"]:
                        new_value = SpecLoader._prompt_param(
                            parameter, prefix="Input value for parameter"
                        )
                        parameter["value"] = new_value
                        result.append(InputParameter(**parameter))
                except Exception as e:
                    raise UpdateParametersError(
                        parameter, step, "Failed Creating Object"
                    ) from e

        return result

    def _update_input(
        self,
        previous: List[InputParameter],
        hub: List[InputParameter],
        debug: bool = False,
    ):
        prev_parameters, hub_parameters, result = self._update_parameters(
            previous, hub
        )
        step = 2
        if debug:
            self._console.print(
                "Updating parameters, we will ask for missing required"
                " parameters if needed."
            )
        for param in hub_parameters.keys():
            if param not in prev_parameters.keys():
                parameter = hub_parameters[param]
                try:
                    if not parameter["value"] and parameter["required"]:
                        new_value = SpecLoader._prompt_param(
                            parameter, prefix="Input value for parameter"
                        )
                        parameter["value"] = new_value
                    result.append(InputParameter(**parameter))
                except Exception as e:
                    raise UpdateParametersError(
                        parameter, step, "Failed Updating Input"
                    ) from e
        return result

    def _update_parameters(
        self,
        previous: List[InputParameter],
        hub: List[Union[InputParameter, Parameter]],
    ) -> List[InputParameter]:
        """
        Create parameters for a new component from lists of InputParameters
        or Parameters. Assumes that equality in name, type and multiple is
        enough to match parameters. In such case the value of the previous
        input is used.
        """
        hub_parameters = {
            (x.name, x.type, x.multiple): {k: v for k, v in x.dict().items()}
            for x in hub
        }
        prev_parameters = {
            (x.name, x.type, x.multiple): {k: v for k, v in x.dict().items()}
            for x in previous
        }
        result = []
        # overwrite hub parameters with previous values
        for param in prev_parameters.keys():
            try:
                if param in hub_parameters.keys():
                    hub_parameters[param]["value"] = prev_parameters[param][
                        "value"
                    ]
                    result.append(InputParameter(**hub_parameters[param]))
            except Exception as e:
                raise UpdateParametersError(hub_parameters[param]) from e
        return prev_parameters, hub_parameters, result

    def _retrieve_component(self, id: str) -> Component:
        try:
            self._console.print("Getting component from engine")
            component = self.db_client.get(Component, id=id, first=True)
        except requests.exceptions.HTTPError as exc:
            raise InvalidComponentId(id) from exc

        if not component:
            raise InvalidComponentId(id)
        return component

    def _update_component(self, component: Component) -> Component:
        updated = self.db_client.save(component)
        return updated

    def _validate_hub_version(
        self,
        from_component: Component,
        version: str,
        check_version: bool = True,
    ) -> HubComponent:
        (
            hub_component_name,
            hub_component_version,
        ) = from_component.version.split("-", 1)
        if check_version and hub_component_version == version:
            raise VersionUpdateError(from_component.name, version)

        manager = self.hubmanager
        try:
            self._console.print(
                f"Getting {hub_component_name} version {version} from hub"
            )
            hub_component = manager.fetch_component_version(
                name=hub_component_name, version=version
            )
        except Exception as e:
            raise HubComponentNotFound(hub_component_name, version) from e
        return hub_component

    def _create_component_objects(
        self, new_component: Component, hub_component: HubComponent
    ):
        self._console.print(
            f"Creating component objects for {new_component.name}"
        )
        old_component_objects = self.db_client.get(
            ComponentObject, component_id=self.component_id
        )
        for obj in old_component_objects:
            try:
                matching_hct = next(
                    (
                        hct
                        for hct in hub_component.custom_types
                        if hct.name == obj.type
                    ),
                    None,
                )
                if matching_hct:
                    new_object_data = self._create_objects(
                        obj.data, matching_hct.fields
                    )
                    new_object = ComponentObject(
                        name=obj.name,
                        type=obj.type,
                        data=new_object_data,
                        component_id=new_component.id,
                    )
                    self.db_client.save(new_object)
                    self._console.print(
                        f"Created {new_object.name} object succesfully"
                    )
            except Exception as e:
                raise ComponentUpgradeManagerException(
                    f"Could not create object {new_object.name}"
                ) from e

    def _create_new_component(
        self,
        from_component: Component,
        hub_component: HubComponent,
        inputs: List[InputParameter],
    ):
        self._console.print(
            "Creating new component"
            f" {from_component.name}-{hub_component.version}"
        )
        new_component = Component(
            name=f"{from_component.name}-{hub_component.version}",
            bindings=hub_component.bindings,
            version=f"{hub_component.name}-{hub_component.version}",
            endpoints=hub_component.endpoints,
            commands=hub_component.commands,
            component_type=hub_component.component_type,
            output=hub_component.output,
            description=hub_component.description,
            custom_types=hub_component.custom_types,
            input=inputs,
        )
        try:
            new_component = self.db_client.save(new_component)
        except Exception as e:
            raise ComponentCreateError(
                new_component.name,
                new_component.version,
                inputs,
                "Could not create new component",
            ) from e
        return new_component

    def upgrade(self, version: str):
        try:
            from_component = self._retrieve_component(self.component_id)
            hub_component = self._validate_hub_version(
                from_component, version, check_version=True
            )
            new_inputs = self._update_input(
                from_component.input, hub_component.input, True
            )
            from_component.input = new_inputs
            new_hub_version = f"{hub_component.name}-{hub_component.version}"
            from_component.version = new_hub_version
            self._update_component(from_component)
            self._create_component_objects(from_component, hub_component)
        except (
            InvalidComponentId,
            VersionUpdateError,
            ComponentCreateError,
            UpdateParametersError,
            HubComponentNotFound,
        ) as e:
            raise ComponentUpgradeManagerException(str(e))

        return from_component

    def clone_component(self, version: Optional[str] = None):
        try:
            from_component = self._retrieve_component(self.component_id)
            hub_name, hub_version = from_component.version.split("-")
            new_version = version if version else hub_version
            hub_component = self._validate_hub_version(
                from_component, new_version, check_version=False
            )
            new_inputs = self._update_input(
                from_component.input, hub_component.input, True
            )
            new_component = self._create_new_component(
                from_component, hub_component, new_inputs
            )
            self._create_component_objects(new_component, hub_component)
        except (
            InvalidComponentId,
            VersionUpdateError,
            ComponentCreateError,
            UpdateParametersError,
            HubComponentNotFound,
        ) as e:
            raise ComponentUpgradeManagerException(str(e))

        return new_component
