from enum import Enum
from pydantic import validator, Field
from typing import List, Dict, Optional
from cli.utils import *
from cli.constants import *
from splight_models import (
    Parameter as ModelParameter,
    InputParameter as ModelInputParameter,
    OutputParameter as ModelOutputParameter,
    CommandParameter as ModelCommandParameter,
    CustomType as ModelCustomType,
    Output as ModelOutput,
    Deployment as ModelDeployment,
    Endpoint as ModelEndpoint
)
from splight_models.constants import ComponentType


class ChoiceMixin:
    @validator("choices", check_fields=False)
    def validate_choices(cls, v, values):
        if "type" not in values:
            return v

        type_ = values["type"]

        if type not in ["str", "int", "float"]:
            raise ValueError("Choices can only be used with string, int or float types")

        # choises type match type field
        try:
            class_type = VALID_PARAMETER_VALUES[type_]
            [isinstance(c, class_type) for c in v]
        except Exception as exc:
            raise ValueError(
                f"choices must be list of type {str(class_type)}"
            ) from exc

        return v


class Parameter(ModelInputParameter, ChoiceMixin):
    @validator("value", check_fields=False)
    def validate_value(cls, v, values, field):
        if not set(values.keys()).issuperset({"type", "required", "multiple", "choices"}):
            return v

        type_ = values["type"]

        # allow custom type
        if type_ not in VALID_PARAMETER_VALUES:
            return v

        # UUIDs and Date must be None
        if VALID_PARAMETER_VALUES[type_] is None:
            return v
        
        # if values["required"] and v is None:
        #     raise ValueError("value must be set")

        # if values["multiple"]:
        #     if not isinstance(v, list):
        #         raise ValueError("value must be a list")

        # Make all parameter values a list
        list_v = v if isinstance(v, list) else [v]

        # value type match type field
        try:
            class_type = VALID_PARAMETER_VALUES[type_]
            [isinstance(v_, class_type) for v_ in list_v]
        except Exception as exc:
            raise ValueError(
                f"value must be of type {str(class_type)}"
            ) from exc

        if values["choices"] is not None and not all([v_ in values["choices"] for v_ in list_v]):
            raise ValueError(f"value must be one of {values['choices']}")

        return v


class OutputParameter(ModelOutputParameter, ChoiceMixin):
    @validator("type", check_fields=False)
    def validate_type(cls, type):
        if type not in VALID_PARAMETER_VALUES:
            raise ValueError(f"invalid output type {type}, can not be custom type")
        return type


class CommandParameter(ModelCommandParameter, ChoiceMixin):
    @validator("type", check_fields=False)
    def validate_type(cls, type):
        if type not in VALID_PARAMETER_VALUES:
            raise ValueError(f"invalid output type {type}, can not be custom type")
        return type


class FieldMixin:
    @validator("fields")
    def validate_fields(cls, fields):
        if len(fields) == 0:
            raise ValueError("fields must not be empty")

        _check_unique_names(fields, "fields")
        _check_parameter_depends_on(fields)

        return fields


class CustomType(ModelCustomType, FieldMixin):
    fields: List[ModelParameter]


class Output(ModelOutput, FieldMixin):
    fields: List[OutputParameter]


class Endpoint(ModelEndpoint):
    name: str
    port: int


class PrivacyPolicy(str, Enum):
    PUBLIC = "public"
    PRIVATE = "private"

    

class Spec(ModelDeployment):
    splight_cli_version: str = Field(regex="^(\d+\.)?(\d+\.)?(\*|\d+)$")
    privacy_policy: PrivacyPolicy = PrivacyPolicy.PUBLIC
    tags: List[str] = []
    component_type: Optional[ComponentType] = ComponentType.CONNECTOR
    custom_types: List[CustomType] = []
    input: List[Parameter] = []
    output: List[Output] = []
    endpoints: List[Endpoint] = []

    @validator("name", check_fields=False)
    def validate_name(cls, name):
        invalid_characters = ["/", "-"]
        if not name[0].isupper():
            raise ValueError("value's first letter must be capitalized")
        if any(x in name for x in invalid_characters):
            raise Exception(f"name cannot contain any of these characters: {invalid_characters}")
        return name

    @validator("version", check_fields=False)
    def validate_version(cls, version):
        invalid_characters = ["/", "-"]
        if len(version) > 20:
            raise Exception("value must be 20 characters maximum")

        if any(x in version for x in invalid_characters):
            raise Exception(f"version cannot contain any of these characters: {invalid_characters}")
        return version

    @validator("tags")
    def validate_tags(cls, tags):
        tag_names = set()
        for tag in tags:
            if tag in tag_names:
                raise Exception(f"Tag name {tag} is not unique")
            tag_names.add(tag)
        return tags

    @validator("custom_types")
    def validate_custom_types(cls, custom_types):
        if custom_types is None:
            return custom_types

        _check_unique_names(custom_types, "custom_types")

        valid_types: List[str] = VALID_PARAMETER_VALUES.keys()
        custom_type_names: List[str] = []

        for custom_type in custom_types:
            for field in custom_type.fields:
                if field.type not in valid_types and field.type not in custom_type_names:
                    raise ValueError(f"custom_type {field.type} not defined")
                if field.name in CustomType._reserved_names:
                    raise ValueError(f"custom_type {field.name} not allowed. Reserved names are: {CustomType._reserved_names}")
            custom_type_names.append(custom_type.name)

        return custom_types

    @validator("input")
    def validate_parameters(cls, v, values, field):
        if "custom_types" not in values:
            return values

        _check_unique_names(v, "input parameters")

        custom_type_names: List[str] = [c.name for c in values["custom_types"]]
        valid_types_names: List[str] = list(VALID_PARAMETER_VALUES.keys()) + custom_type_names

        for parameter in v:
            if parameter.type not in valid_types_names:
                raise ValueError(f"input type {parameter.type} not defined")

        # depends on
        _check_parameter_depends_on(v)
        return v

    @validator("output")
    def validate_output(cls, v, values, field):
        _check_unique_names(v, "output parameters")
        return v
    
    @classmethod
    def verify(cls, dict: dict):
        cls(**dict)


def _check_parameter_depends_on(parameters: List[Parameter]):
    parameter_map: Dict[str, Parameter] = {p.name: p for p in parameters}
    for parameter in parameters:
        if not parameter.depends_on:
            continue

        if parameter.depends_on not in parameter_map:
            raise ValueError(f"depends_on must be one of {parameter_map.keys()}")

        depend_parameter = parameter_map[parameter.depends_on]

        if (parameter.type, depend_parameter.type) not in VALID_DEPENDS_ON:
            raise ValueError(f"incompatible dependance: type {parameter.type} can not"
                             f"depend on type {depend_parameter.type}")


def _check_unique_names(parameters: List[Parameter], type: str):
    parameters_names = [p.name for p in parameters]
    if len(parameters) != len(set(parameters_names)):
        raise ValueError(f"{type} must have unique names")
