import json
from typing import Dict, List, Union

from cli.utils import get_json_from_file, input_single

Primitive = Union[int, str, float, bool]


class SpecArgumentLoader:
    def __init__(self, spec_json: str):
        self._spec_json = spec_json

    def load_spec(self) -> Dict:
        run_spec = json.loads(self._spec_json)
        return run_spec


class SpecJSONLoader:

    _CT_KEY: str = "custom_types"
    _INPUT_KEY: str = "input"
    _OUTPUT_KEY: str = "output"
    _COMMANDS_KEY: str = "commands"

    def __init__(
        self,
        spec_file_path: str,
        check_input: bool = True,
    ):
        self._spec_file_path = spec_file_path
        self._check_input = check_input

    def load_spec(self) -> Dict:
        raw_spec = get_json_from_file(self._spec_file_path)
        input_parameters = raw_spec[self._INPUT_KEY]
        if self._check_input:
            input_parameters = self._load_or_prompt_input(input_parameters)

        full_spec = raw_spec
        full_spec["input"] = input_parameters
        return full_spec

    def _load_or_prompt_input(
        self,
        input_params: List[Dict],
        prefix: str = "",
    ):
        for param in input_params:
            value = param.get("value")
            if not value:
                new_value = self._prompt_param(param, prefix=prefix)
                param["value"] = new_value

        return input_params

    def _prompt_param(
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
