from pydantic import BaseModel, validator
from typing import List, Union, Optional
from ..utils import *
from cli.settings import *
from splight_models import Deployment


class Parameter(BaseModel):
    name: str
    type: str
    required: bool
    multiple: bool = False
    choices: Union[List[str], List[int], List[float], None] = None
    value: Union[str, int, float, bool, UUID, list, None]

    @validator("value")
    def validate_value(cls, v, values, field):
        if "type" not in values:
            return values

        type_ = values["type"]

        # allow custom type
        if type_ not in VALID_PARAMETER_VALUES:
            if v is not None:
                raise ValueError(f"custom types value must be None")
            return v

        # UUIDs and Date must be None
        if VALID_PARAMETER_VALUES[type_] is None or type_ == "Date":
            if v is not None:
                raise ValueError(f"value must be None")
            return v

        if values["required"] and v is None:
            raise ValueError(f"value must be set")

        if values["multiple"]:
            if not isinstance(v, list):
                raise ValueError(f"value must be a list")

        list_v = v if isinstance(v, list) else [v]

        # value type match type field
        try:
            class_type = VALID_PARAMETER_VALUES[type_]
            [isinstance(v_, class_type) for v_ in list_v]
        except Exception as e:
            raise ValueError(f"value must be of type {str(class_type)}")

        if values["choices"] is not None and not all([v_ in values["choices"] for v_ in list_v]):
            raise ValueError(f"value must be one of {values['choices']}")

        return v


class CustomType(BaseModel):
    name: str
    fields: List[Parameter]

    @validator("fields")
    def validate_fields(cls, fields):
        if len(fields) == 0:
            raise ValueError("fields must not be empty")

        field_names = [f.name for f in fields]
        if len(fields) != len(set(field_names)):
            raise ValueError("fields must have unique names")

        return fields


class SpecDeployment(Deployment):
    custom_types: List[CustomType]
    parameters: List[Parameter]
    name: str

    @validator("name", check_fields=False)
    def validate_name(cls, name):
        invalid_characters = ["/", "-"]
        if not name[0].isupper():
            raise ValueError(f"value's first letter must be capitalized")
        if any(x in name for x in invalid_characters):
            raise Exception(f"value cannot contain any of these characters: {invalid_characters}")
        return name

    @validator("version", check_fields=False)
    def validate_version(cls, version):
        invalid_characters = ["/", "-"]
        if len(version) > 20:
            raise Exception(f"value must be 20 characters maximum")

        if any(x in version for x in invalid_characters):
            raise Exception(f"value cannot contain any of these characters: {invalid_characters}")
        return version

    @validator("custom_types", check_fields=False)
    def validate_custom_types(cls, custom_types):
        if custom_types is None:
            return custom_types

        valid_types: List[str] = VALID_PARAMETER_VALUES.keys()
        custom_type_names: List[str] = []

        for custom_type in custom_types:
            for field in custom_type.fields:
                if field.type not in valid_types and field.type not in custom_type_names:
                    raise ValueError(f"custom_type {field.type} not defined")
            custom_type_names.append(custom_type.name)

        if len(custom_types) != len(set(custom_type_names)):
            raise ValueError("custom_types must have unique names")

        return custom_types

    @validator("parameters", check_fields=False)
    def validate_parameters(cls, v, values, field):
        if "custom_types" not in values:
            return values

        parameters_names: List[str] = [p.name for p in v]

        if len(v) != len(set(parameters_names)):
            raise ValueError("parameters must have unique names")

        custom_type_names: List[str] = [c.name for c in values["custom_types"]]
        valid_types_names: List[str] = VALID_PARAMETER_VALUES.keys()

        for parameter in v:
            if parameter.type not in valid_types_names and parameter.type not in custom_type_names:
                raise ValueError(f"parameter type {parameter.type} not defined")

        return v
