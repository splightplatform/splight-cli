import importlib
import os
import sys
import subprocess
from typing import Dict, List, Union, Optional
from splight_lib.component import AbstractComponent
from splight_lib import logging
from cli.component.spec import Spec
from cli.constants import (
    MAIN_CLASS_NAME,
    SPEC_FILE,
    COMPONENT_FILE, 
    SPEC_FILE,
    INIT_FILE,
    README_FILE_1,
    README_FILE_2
)
from cli.utils import get_json_from_file, input_single

logger = logging.getLogger()
Primitive = Union[int, str, float, bool]


class ComponentLoader:
    _MAIN_CLASS_NAME: str = "Main"
    REQUIRED_FILES = [
        COMPONENT_FILE, SPEC_FILE, INIT_FILE, README_FILE_1
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
        for required_file in [x for x in self.REQUIRED_FILES if x!=README_FILE_1]:
            if not os.path.isfile(os.path.join(self.base_path, required_file)):
                raise Exception(
                    f"{required_file} file is missing in {self.base_path}"
                )
        # retrocompatibility for components with README without extension
        if not os.path.isfile(os.path.join(self.base_path, README_FILE_1)) \
            and not os.path.isfile(os.path.join(self.base_path, README_FILE_2)):
                raise Exception(
                    f"No {README_FILE_1} or {README_FILE_2} found in {self.base_path}"
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
    _COMPONENT_KEY: str = "component_type"
    _CT_KEY: str = "custom_types"
    _INPUT_KEY: str = "input"
    _OUTPUT_KEY: str = "output"
    _BINDINGS_KEY: str = "bindings"
    _COMMANDS_KEY: str = "commands"
    _ENDPOINTS_KEY: str = "endpoints"

    def __init__(self, path: str):
        self.raw_spec = get_json_from_file(os.path.join(path, SPEC_FILE))
        self._validate()

    def load(self, input_parameters: Optional[List[Dict]] = None, prompt_input = True):
        input_parameters = input_parameters if input_parameters else self.raw_spec['input']
        if prompt_input:
            input_parameters = self._load_or_prompt_input(input_parameters)
        self.raw_spec["input"] = input_parameters
        self._validate()
        return Spec.parse_obj(self.raw_spec)

    def _load_or_prompt_input(
        self,
        input_parameters: List[Dict],
        prefix: str = "",
    ):
        for param in input_parameters:
            value = param.get("value")
            if value is None:
                new_value = self._prompt_param(param, prefix=prefix)
                param["value"] = new_value

        return input_parameters

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


class InitLoader:
    def __init__(self, path: str) -> None:
        self.path = path
        self._validate()

    def _handle_RUN(self, command: List[str]) -> None:
        command: str = " ".join(command)
        logger.debug(f"Running initialization command: {command} ...")
        try:
            subprocess.run(command, check=True, cwd=self.path, shell=True)
        except subprocess.CalledProcessError as e:
            raise Exception(
                f"Failed to run command: {e.cmd}. Output: {e.output}"
            )

    def _load_commands(self) -> List[List[str]]:
        file = os.path.join(self.path, INIT_FILE)
        lines: List[str] = []
        lines.append(["RUN", "pip", "cache", "purge"])
        with open(file) as f:
            for line in f:
                line = line.strip()
                if line.startswith("#") or line == "":
                    continue
                lines.append(line.split(" "))
        return lines

    def load(self):
        commands = self._load_commands()
        for command in commands:
            prefix: str = command[0]
            handler = getattr(self, f'_handle_{prefix}', None)
            if not handler:
                raise Exception(f"Invalid command: {prefix}")
            handler(command[1:])

    def _validate(self):
        # VALIDATE FILES
        if not os.path.isfile(os.path.join(self.path, INIT_FILE)):
            raise Exception(
                f"{INIT_FILE} file is missing in {self.path}"
            )
