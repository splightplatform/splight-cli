import importlib
import os
import sys
from typing import Dict, List, Union, Optional
from splight_lib.component import AbstractComponent

from cli.component.spec import Spec
from cli.constants import MAIN_CLASS_NAME, SPEC_FILE, COMPONENT_FILE, SPEC_FILE, INIT_FILE, README_FILE
from cli.utils import get_json_from_file, input_single


Primitive = Union[int, str, float, bool]


class ComponentLoader:
    _MAIN_CLASS_NAME: str = "Main"
    REQUIRED_FILES = [
        COMPONENT_FILE, SPEC_FILE, INIT_FILE, README_FILE
    ]

    def __init__(self, path: str) -> None:
        self.base_path = path
        self.component_directory_name = path.split(os.sep)[-1]
        self.module = None
        sys.path.append(os.path.dirname(path))
        self._validate()

    def load(self):
        try:
            self.module = importlib.import_module(self.component_directory_name)
        except Exception as e:
            raise Exception(
                f"Failed importing component {self.component_directory_name}: {str(e)}"
            ) from e
        self._validate()
        self.main_class = getattr(self.module, MAIN_CLASS_NAME)
        return self.main_class

    def _validate(self):
        # VALIDATE FILES
        for required_file in self.REQUIRED_FILES:
            if not os.path.isfile(os.path.join(self.base_path, required_file)):
                raise Exception(
                    f"{required_file} file is missing in {self.base_path}"
                )
        if self.module:
            # VALIDATE MODULE HAS MAIN CLASS
            if not hasattr(self.module, MAIN_CLASS_NAME):
                raise Exception(
                    f"Component does not have a class called {MAIN_CLASS_NAME}"
                )
            # VALIDATE MAIN CLASS IS INHERITING FROM ABSTRACTCOMPONENT
            if not any(
                [
                    parent_class.__name__ == AbstractComponent.__name__
                    for parent_class in getattr(self.module, MAIN_CLASS_NAME).__mro__
                ]
            ):
                raise Exception(
                    f"Component class {MAIN_CLASS_NAME} must inherit from one of Splight's component classes"
                )


class SpecLoader:
    _NAME_KEY: str = "name"
    _VERSION_KEY: str = "version"
    _SPLIGHT_CLI_VERSION_KEY: str = "splight_cli_version"
    _PRIVACY_POLICY_KEY: str = "privacy_policy"

    _CT_KEY: str = "custom_types"
    _INPUT_KEY: str = "input"
    _OUTPUT_KEY: str = "output"
    _BINDINGS_KEY: str = "bindings"
    _COMMANDS_KEY: str = "commands"
    _ENDPOINTS_KEY: str = "endpoints"

    def __init__(self, path: str):
        self.raw_spec = get_json_from_file(os.path.join(path, SPEC_FILE))
        self._validate()

    def load(self, input_parameters: Optional[List[Dict]] = None):
        input_parameters = input_parameters if input_parameters else self.raw_spec['input']
        input_parameters = self._load_or_prompt_input(input_parameters)
        self.raw_spec["input"] = input_parameters
        self._validate()
        return Spec.parse_obj(self.raw_spec)

    def _load_or_prompt_input(
        self,
        input_params: List[Dict],
        prefix: str = "",
    ):
        for param in input_params:
            value = param.get("value")
            if value is None:
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

    def _validate(self):
        Spec.verify(self.raw_spec)
