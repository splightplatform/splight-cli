import json
import os
import shutil
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional, Type, Union

import pandas as pd
from pydantic import BaseModel
from rich.console import Console
from rich.table import Table
from splight_lib.models import (
    Component,
    ComponentObject,
    File,
    HubComponent,
    RoutineObject,
)
from splight_lib.models.base import (
    SplightDatabaseBaseModel,
    SplightDatalakeBaseModel,
)
from splight_lib.models.component import (
    DataAddress,
    InputDataAddress,
    InputParameter,
    Parameter,
)

from splight_cli.component.exceptions import InvalidCSVColumns
from splight_cli.constants import (
    REQUIRED_DATALAKE_COLUMNS,
    success_style,
    warning_style,
)
from splight_cli.engine.manager.exceptions import (
    ComponentCreateError,
    InvalidComponentId,
    UpdateParametersError,
    VersionUpdateError,
)
from splight_cli.hub.component.exceptions import HubComponentNotFound
from splight_cli.utils.input import prompt_data_address_value, prompt_param

SplightModel = Type[SplightDatabaseBaseModel]


class ResourceManagerException(Exception):
    pass


class DatalakeManagerException(Exception):
    pass


class ComponentUpgradeManagerException(Exception):
    def __init__(self, message: str):
        self.message = message

    def __str__(self):
        return self.message


class QueryParam(BaseModel):
    value: Union[List[int], List[float], List[str], int, float, str]


class ResourceManager:
    def __init__(
        self,
        model: SplightDatabaseBaseModel,
    ):
        self._model = model
        self._resource_name = model.__name__
        self._console = Console()

    def get(
        self, instance_id: str, exclude_fields: Optional[List[str]] = None
    ):
        exclude_fields = exclude_fields if exclude_fields is not None else []
        instance = self._model.retrieve(resource_id=instance_id)
        if not instance:
            raise ResourceManagerException(
                f"No {self._model.__name__} found with ID = {instance_id}"
            )

        name = instance.name if hasattr(instance, "name") else instance.title
        table = Table(
            title=f"{self._resource_name} = {name}", show_header=False
        )
        _ = [
            table.add_row(key, str(value))
            for key, value in instance.model_dump().items()
            if key not in exclude_fields
        ]
        self._console.print(table)

    def list(self, params: Dict[str, Any]):
        instances = self._model.list(**params)

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
        instance = self._model.model_validate(data)
        instance.save()

        table = Table(
            title=f"{self._resource_name} = {getattr(instance,'name', '')}",
            show_header=False,
        )
        _ = [
            table.add_row(key, str(value))
            for key, value in instance.model_dump().items()
        ]
        self._console.print(table)

    def delete(self, instance_id: str):
        self._model.retrieve(resource_id=instance_id).delete()
        self._console.print(
            f"{self._resource_name}={instance_id} deleted", style=warning_style
        )

    def download(self, instance_id: str, path: str):
        instance = self._model.retrieve(instance_id)
        if isinstance(instance, File):
            file_path = os.path.join(path, instance.name)
            downloaded = instance.download()
            shutil.copy(downloaded.name, file_path)
        else:
            file_path = os.path.join(
                path, f"{instance.__class__.__name__}-{instance.id}.json"
            )
            with open(file_path, "w") as fid:
                json.dump(instance.model_dump(), fid, indent=2)

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
        model: SplightDatalakeBaseModel,
    ):
        self._model = model
        self._console = Console()

    def dump(self, path, filters):
        if os.path.exists(path):
            raise Exception(f"File {path} already exists")
        if os.path.isdir(path):
            path = os.path.join(path, "splight_dump.csv")
        elif not path.endswith(".csv"):
            raise Exception("Only CSV files are supported")

        dataframe = self._model.get_dataframe(**self._get_filters(filters))
        dataframe.to_csv(path)
        self._console.print(
            f"Succesfully dumpped {self._model.__name__}'s in {path}",
            style=success_style,
        )

    def load(self, path: str):
        if not os.path.isfile(path):
            raise Exception("File not found")
        if not path.endswith(".csv"):
            raise Exception("Only CSV files are supported")

        dataframe = pd.read_csv(path)
        self._validate_csv(dataframe)
        dataframe = dataframe.set_index("timestamp")
        self._model.save_dataframe(dataframe)
        self._console.print(
            f"Succesfully loaded {path} in {self._model.__name__}",
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
    def __init__(self, component_id: str):
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
                        new_value = prompt_param(
                            parameter, prefix="Input value for parameter"
                        )
                        parameter["value"] = new_value
                        result.append(InputParameter(**parameter))
                except Exception as e:
                    raise UpdateParametersError(
                        parameter, step, "Failed Creating Object"
                    ) from e

        return result

    def _update_routine_io(
        self,
        engine_io: List[InputDataAddress],
        hub_io: List[InputDataAddress],
        routine_name: str,
        routine_type: str,
        source: Union[Literal["input"], Literal["output"]],
        debug: bool = False,
    ):
        # Basically create new InputDataAddress from the definitions
        # of each input, in the new hub version, while assigning the
        # previous value to matching inputs or outputs.
        # i.e: update the 'required' key of an input.
        (
            engine_data_addresses,
            hub_data_addresses,
            result,
        ) = self._update_data_address(engine_io, hub_io)
        step = 2
        if debug:
            self._console.print(
                "Updating parameters, we will ask for missing required"
                " parameters if needed."
            )

        # Ask for a missing InputDataAddress
        for name in hub_data_addresses.keys():
            if name not in engine_data_addresses.keys():
                hub_data_address = hub_data_addresses[name]
                try:
                    if "value" not in hub_data_address.keys():
                        self._console.print(
                            f"Insert values for {source} '{name[0]}' of routine '{routine_name}' ({routine_type}):"
                        )
                        new_value = prompt_data_address_value()
                        hub_data_address["value"] = new_value
                    result.append(InputDataAddress(**hub_data_address))
                except Exception as e:
                    raise UpdateParametersError(
                        hub_data_address, step, "Failed Updating Input"
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
                        new_value = prompt_param(
                            parameter, prefix="Input value for parameter"
                        )
                        parameter["value"] = new_value
                    result.append(InputParameter(**parameter))
                except Exception as e:
                    raise UpdateParametersError(
                        parameter, step, "Failed Updating Input"
                    ) from e
        return result

    def _update_routine_config(
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
                    if (
                        "value" not in parameter.keys()
                        and parameter["required"]
                    ):
                        new_value = prompt_param(
                            parameter, prefix="Input value for routine config"
                        )
                        parameter["value"] = new_value
                    result.append(InputParameter(**parameter))
                except Exception as e:
                    raise UpdateParametersError(
                        parameter, step, "Failed Updating Input"
                    ) from e
        return result

    def _update_data_address(
        self,
        previous: List[InputDataAddress],
        hub: List[Union[InputDataAddress, DataAddress]],
    ):
        hub_parameters = {
            (x.name, x.type): {k: v for k, v in x.model_dump().items()}
            for x in hub
        }
        prev_parameters = {
            (x.name, x.type): {k: v for k, v in x.model_dump().items()}
            for x in previous
        }
        result = []
        for param in prev_parameters.keys():
            try:
                if param in hub_parameters.keys():
                    hub_parameters[param]["value"] = prev_parameters[param][
                        "value"
                    ]
                    result.append(InputDataAddress(**hub_parameters[param]))
            except Exception as e:
                raise UpdateParametersError(hub_parameters[param]) from e
        return prev_parameters, hub_parameters, result

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
            (x.name, x.type, x.multiple): {
                k: v for k, v in x.model_dump().items()
            }
            for x in hub
        }
        prev_parameters = {
            (x.name, x.type, x.multiple): {
                k: v for k, v in x.model_dump().items()
            }
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
            component = Component.retrieve(resource_id=id)
        except Exception as exc:
            raise InvalidComponentId(id) from exc
        return component

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

        try:
            self._console.print(
                f"Getting {hub_component_name} version {version} from hub"
            )
            hub_component = HubComponent.list_all(
                name=hub_component_name, version=version
            )
        except Exception as exc:
            raise HubComponentNotFound(hub_component_name, version) from exc
        if not hub_component:
            raise HubComponentNotFound(hub_component_name, version)
        return hub_component[0]

    def _create_component_objects(
        self,
        new_component: Component,
        hub_component: HubComponent,
        create_new: bool = False,
    ):
        self._console.print(
            f"Creating component objects for component '{new_component.name}'"
        )
        old_component_objects = ComponentObject.list(
            component_id=self.component_id
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
                    if create_new:
                        new_object = ComponentObject(
                            name=obj.name,
                            type=obj.type,
                            data=new_object_data,
                            component_id=new_component.id,
                        )
                        new_object.save()
                    else:
                        obj.data = new_object_data
                        obj.save()
                    self._console.print(
                        f"Component Object {obj.name} saved succesfully"
                    )
            except Exception as e:
                raise ComponentUpgradeManagerException(
                    f"Could not update component object {obj.name}"
                ) from e

    def _create_component_routines(
        self,
        new_component: Component,
        hub_component: HubComponent,
        create_new: bool = False,
    ):
        self._console.print(
            f"Creating routines for component '{new_component.name}'"
        )
        routines = RoutineObject.list(component_id=self.component_id)

        for routine in routines:
            try:
                matching_routine = next(
                    (
                        hub_routine
                        for hub_routine in hub_component.routines
                        if hub_routine.name == routine.type
                    ),
                    None,
                )
                if matching_routine:
                    new_inputs = self._update_routine_io(
                        routine.input,
                        matching_routine.input,
                        routine.name,
                        routine.type,
                        source="input",
                    )
                    new_outputs = self._update_routine_io(
                        routine.output,
                        matching_routine.output,
                        routine.name,
                        routine.type,
                        source="output",
                    )
                    new_configs = self._update_routine_config(
                        routine.config, matching_routine.config
                    )
                    if create_new:
                        new_routine = RoutineObject(
                            name=routine.name,
                            component_id=new_component.id,
                            status=routine.status,
                            type=routine.type,
                            description=routine.description,
                            input=new_inputs,
                            output=new_outputs,
                            config=new_configs,
                        )
                        new_routine.save()
                    else:
                        routine.input = new_inputs
                        routine.output = new_outputs
                        routine.config = new_configs
                        routine.save()
                    self._console.print(
                        f"Routine '{routine.name}' saved succesfully"
                    )

            except Exception as e:
                raise ComponentUpgradeManagerException(
                    f"Could not update component routine {routine.name}: {e}"
                ) from e
        return

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
            version=f"{hub_component.name}-{hub_component.version}",
            endpoints=hub_component.endpoints,
            component_type=hub_component.component_type,
            output=hub_component.output,
            description=hub_component.description,
            custom_types=hub_component.custom_types,
            input=inputs,
        )
        try:
            new_component.save()
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
            from_component.save()
            self._create_component_objects(
                from_component, hub_component, create_new=False
            )
            self._create_component_routines(
                from_component, hub_component, create_new=False
            )

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
            self._create_component_objects(
                new_component, hub_component, create_new=True
            )
            self._create_component_routines(
                new_component, hub_component, create_new=True
            )
        except (
            InvalidComponentId,
            VersionUpdateError,
            ComponentCreateError,
            UpdateParametersError,
            HubComponentNotFound,
        ) as e:
            raise ComponentUpgradeManagerException(str(e))

        return new_component
