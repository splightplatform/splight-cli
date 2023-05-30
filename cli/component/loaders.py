import os
import subprocess
from typing import Dict, List, Optional, Union

from splight_lib.logging._internal import get_splight_logger

from cli.component.spec import Spec
from cli.constants import INIT_FILE, SPEC_FILE
from cli.utils import get_json_from_file, input_single

logger = get_splight_logger()
Primitive = Union[int, str, float, bool]


class SpecLoader:
    _NAME_KEY: str = "name"
    _VERSION_KEY: str = "version"
    _DESCRIPTION_KEY: str = "description"
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

    def load(
        self,
        input_parameters: Optional[List[Dict]] = None,
        prompt_input: bool = True,
    ):
        input_parameters = (
            input_parameters if input_parameters else self.raw_spec["input"]
        )
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

    @staticmethod
    def _prompt_param(param: Dict, prefix: str = "") -> Primitive:
        """Prompt the user for a single parameter

        Parameters
        ----------
        param: Dict
            The parameter to prompt
        prefix: str
            Prefix for the parameter name

        Returns
        -------
        Primitive
        """
        param_name = param["name"]
        new_value = input_single(
            {
                "name": f"{prefix} {param_name}",
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
            handler = getattr(self, f"_handle_{prefix}", None)
            if not handler:
                raise Exception(f"Invalid command: {prefix}")
            handler(command[1:])

    def _validate(self):
        # VALIDATE FILES
        if not os.path.isfile(os.path.join(self.path, INIT_FILE)):
            raise Exception(f"{INIT_FILE} file is missing in {self.path}")
