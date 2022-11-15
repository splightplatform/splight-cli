import json
from typing import Dict, List, Union

from cli.utils import get_json_from_file, input_single

Primitive = Union[int, str, float, bool]


class SpecArgumentLoader:
    def __init__(self, spec_json: str, component_type: str):
        self._component_type = component_type.title()
        self._spec_json = spec_json

    def load_spec(self) -> Dict:
        run_spec = json.loads(self._spec_json)
        run_spec["type"] = self._component_type
        return run_spec


class SpecJSONLoader:

    _CT_KEY: str = "custom_types"
    _INPUT_KEY: str = "input"
    _OUTPUT_KEY: str = "output"

    def __init__(
        self,
        spec_file_path: str,
        component_type: str,
        check_input: bool = True,
    ):
        self._component_type = component_type.title()
        self._spec_file_path = spec_file_path
        self._check_input = check_input

    def load_spec(self) -> Dict:
        raw_spec = get_json_from_file(self._spec_file_path)
        custom_types = [value["name"] for value in raw_spec[self._CT_KEY]]
        input_parameters = raw_spec[self._INPUT_KEY]

        if self._check_input:
            input_parameters = self._check_input_values(
                input_parameters, custom_types
            )

        full_spec = raw_spec
        full_spec["type"] = self._component_type
        full_spec["input"] = input_parameters
        return full_spec

    def _check_input_values(
        self,
        input_params: List[Dict],
        custom_types: List[str],
        prefix: str = "",
    ):
        for param in input_params:
            param_type = param["type"]
            value = param.get("value")
            if not value:
                new_value = self._read_value_from_prompt(param, prefix=prefix)
                param["value"] = new_value

            if param_type in custom_types:
                self._check_custom_type_input(
                    param, custom_types, prefix=prefix
                )

        return input_params

    def _check_custom_type_input(
        self,
        param: Union[List[Dict], Dict],
        custom_types: List[str],
        prefix: str = "",
    ):
        multiple = param["multiple"]
        param_name = param["name"]
        if multiple:
            for idx, sub_param in enumerate(param["value"]):
                self._check_input_values(
                    sub_param,
                    custom_types,
                    prefix=f"{prefix}.{param_name}[{idx}]",
                )
        else:
            self._check_input_values(
                param["value"], custom_types, prefix=f"{prefix}.{param_name}"
            )

    def _read_value_from_prompt(
        self, param: Dict, prefix: str = ""
    ) -> Primitive:
        param_name = param["name"]
        new_value = input_single(
            {
                "name": f"{prefix}.{param_name}",
                "type": param["type"],
                "required": param.get("required", True),
                "multiple": param.get("multiple", False),
                "value": param.get("value"),
            }
        )
        return new_value
