import logging
from unittest.mock import Base
from numpy import isin
from pydantic import BaseModel, validator, create_model
from typing import Type, List, Any, Optional, Dict, Tuple, Literal
from ..utils import *
from cli.settings import *
from copy import copy
from enum import Enum
from .description_spec import DescriptionSpec


logger = logging.getLogger()


class InputSpec(BaseModel):
    type: str
    namespace: str
    external_id: str
    custom_types: List[Type]
    parameters: BaseModel


class InputSpecFactory:
    def __init__(self, spec_structure: DescriptionSpec) -> None:
        self.type_map = self._load_type_map()
        self._custom_types_models = self._get_custom_types_models(spec_structure)
        self._parametes_model = self._get_parameters_model(spec_structure)
        self._custom_types_names = [custom_type.__name__ for custom_type in self._custom_types_models]

    def get_input_spec(self, run_spec: Dict) -> InputSpec:
        parameters = self._parse_parameter(run_spec["parameters"])
        return InputSpec(
            type=run_spec["type"],
            namespace=run_spec["namespace"],
            external_id=run_spec["external_id"],
            custom_types=self._custom_types_models,
            parameters=self._parametes_model(**parameters),
        )

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

    def _load_type_map(self) -> Dict[str, Type]:
        type_map: Dict[str, Type] = copy(VALID_PARAMETER_VALUES)
        for key, value in type_map.items():
            if value is None:
                type_map[key] = str
        return type_map

    def _get_custom_types_models(self, spec_structure: DescriptionSpec) -> List[BaseModel]:
        if not spec_structure.custom_types:
            return []

        custom_types: List[Type] = []

        for custom_type in spec_structure.custom_types:
            fields: Dict[str, Tuple] = {}

            for field in custom_type.fields:
                type = self.type_map[field.type]

                if field.multiple:
                    type = List[type]

                if field.choices:
                    type = Enum(f"{field.name}-choices", {str(p): p for p in field.choices})

                value = field.value if field.value is not None else ...
                fields[field.name] = (type, value)

            model = create_model(custom_type.name, **fields)

            self.type_map[custom_type.name] = model
            custom_types.append(model)

        return custom_types

    def _get_parameters_model(self, spec_structure: DescriptionSpec) -> BaseModel:
        fields: Dict[str, Tuple] = {}

        for parameter in spec_structure.parameters:
            type = self.type_map[parameter.type]

            if parameter.multiple:
                type = List[type]

            if parameter.choices:
                type = Enum(f"{parameter.name}-choices", {str(p): p for p in parameter.choices})

            value = parameter.value if parameter.value is not None else ...
            fields[parameter.name] = (type, value)

        return create_model("Parameters", **fields)
