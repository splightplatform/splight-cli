import logging
from pydantic import BaseModel, create_model
from typing import Type, List, Dict, Tuple
from ..utils import *
from cli.settings import *
from copy import copy
from enum import Enum
from splight_lib.database import DatabaseClient
from splight_lib.storage import StorageClient
from .description_spec import SpecDeployment
from splight_models import *
from pprint import pprint as print
logger = logging.getLogger()


def props(cls):
    return [i for i in cls.__dict__.keys() if not i.startswith('__')]


class InputDeploymentFactory:
    def __init__(self, spec_structure: SpecDeployment) -> None:
        self.type = spec_structure.type
        self.name = spec_structure.name
        self.version = spec_structure.version

        self._type_map = self._load_type_map()
        self._custom_types_model = self._get_custom_types_model(spec_structure)
        self._parametes_model = self._get_parameters_model(spec_structure)
        self._custom_types_names = props(self._custom_types_model)

    def get_input_deployment(self, run_spec: Dict) -> InputDeployment:
        namespace = run_spec["namespace"]
        exeternal_id = run_spec["external_id"]
        self._database_client = DatabaseClient(namespace)
        self._storage_client = StorageClient(namespace)

        parameters = run_spec["parameters"]
        parameters = self._retrive_objects_from_id(parameters)
        parameters = self._parse_parameter(parameters)
        return InputDeployment(
            version=self.name + "-" + self.version,
            type=self.type,
            namespace=namespace,
            external_id=exeternal_id,
            custom_types=self._custom_types_model,
            parameters=self._parametes_model(**parameters),
        )

    def _load_type_map(self) -> Dict[str, Type]:
        type_map: Dict[str, Type] = copy(VALID_PARAMETER_VALUES)
        type_map.update(DATABASE_TYPES)
        type_map.update(STORAGE_TYPES)

        return type_map

    def _retrive_objects_from_id(self, parameters: List):
        ids = {
            "database": defaultdict(list),
            "storage": defaultdict(list),
        }
        self._get_ids(parameters, ids)
        objects = self._retrieve_objects(ids)
        self._complete_parameters_with_objects(parameters, objects)
        return parameters

    def _get_ids(self, parameters: List, ids: Dict) -> None:
        for parameter in parameters:
            values = parameter["value"] if parameter["multiple"] else [parameter["value"]]

            if parameter["type"] in DATABASE_TYPES:
                for value in values:
                    ids["database"][parameter["type"]].append(value)
            elif parameter["type"] in STORAGE_TYPES:
                for value in values:
                    ids["storage"][parameter["type"]].append(value)
            elif parameter["type"] in self._custom_types_names:
                for value in values:
                    self._get_ids(value, ids)

    def _retrieve_objects(self, ids: Dict) -> Dict[str, BaseModel]:
        res: Dict = {}
        for type, ids_ in ids["database"].items():
            objs = self._database_client.get(DATABASE_TYPES[type], id__in=ids_)
            res.update({obj.id: obj for obj in objs})

        for type, ids_ in ids["storage"].items():
            objs = self._storage_client.get(STORAGE_TYPES[type], id__in=ids_)
            res.update({obj.id: obj for obj in objs})

        return res

    def _complete_parameters_with_objects(self, parameters: List, objects: Dict) -> None:
        for parameter in parameters:

            if parameter["type"] in DATABASE_TYPES or parameter["type"] in STORAGE_TYPES:
                if parameter["multiple"]:
                    parameter["value"] = [objects[val] for val in parameter["value"]]
                else:
                    parameter["value"] = objects[parameter["value"]]

            elif parameter["type"] in self._custom_types_names:
                values = parameter["value"] if parameter["multiple"] else [parameter["value"]]
                for value in values:
                    self._complete_parameters_with_objects(value, objects)

    def _parse_parameter(self, parameters: List) -> Dict:
        parameters_dict: Dict = {}
        for parameter in parameters:
            type = parameter["type"]
            name = parameter["name"]
            value = parameter["value"]
            multiple = parameter["multiple"]

            if type not in self._custom_types_names:
                parameters_dict[name] = value
            elif multiple:
                parameters_dict[name] = [self._parse_parameter(val) for val in value]
            else:
                parameters_dict[name] = self._parse_parameter(value)

        return parameters_dict

    def _get_custom_types_model(self, spec_structure: SpecDeployment) -> List[BaseModel]:
        if not spec_structure.custom_types:
            return []

        custom_types: Dict[str, BaseModel] = {}

        for custom_type in spec_structure.custom_types:
            model = self._create_model(custom_type.name, custom_type.fields)
            custom_types[custom_type.name] = model
            self._type_map[custom_type.name] = model

        return type("CustomTypes", (), custom_types)

    def _get_parameters_model(self, spec_structure: SpecDeployment) -> BaseModel:
        return self._create_model("Parameters", spec_structure.parameters)

    def _create_model(self, name: str, fields: List):
        fields_dict: Dict[str, Tuple] = {}
        for field in fields:
            type = self._type_map[field.type]

            if field.choices:
                type = Enum(f"{field.name}-choices", {str(p): p for p in field.choices})

            if field.multiple:
                type = List[type]

            value = field.value if field.value is not None else ...
            fields_dict[field.name] = (type, value)

        return create_model(name, **fields_dict)
