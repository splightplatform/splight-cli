import json
import os
import subprocess
from enum import auto
from pathlib import Path
from typing import List, Optional

from caseconverter import pascalcase
from jinja2 import Template
from rich.console import Console
from splight_lib.component.spec import Spec
from strenum import LowercaseStrEnum

from cli.component.exceptions import (
    InvalidSplightCLIVersion,
    ReadmeExists,
    ComponentExecutionError,
)
from cli.component.loaders import (
    InitLoader,
)
from cli.constants import (
    COMPONENT_FILE,
    INIT_FILE,
    README_FILE,
    SPEC_FILE,
    SPLIGHT_IGNORE,
    TESTS_FILE,
)
from cli.utils import get_template
from cli.version import __version__


console = Console()


class AvailableLanguages(LowercaseStrEnum):
    PYTHON = auto()


BASE_COMMANDS = {AvailableLanguages.PYTHON: ["python", "main.py"]}


class ComponentManager:

    _COMPONENT_REQUIRED_FILES = [
        COMPONENT_FILE,
        INIT_FILE,
        README_FILE,
        SPEC_FILE,
        SPLIGHT_IGNORE,
        TESTS_FILE,
    ]

    def create(
        self, name: str, version: str = "0.1.0", component_path: str = "."
    ):
        component_name = pascalcase(name)
        absolute_path = os.path.abspath(component_path)
        if not os.path.exists(absolute_path):
            os.makedirs(absolute_path)

        for file_name in self._COMPONENT_REQUIRED_FILES:
            template_name = file_name
            file_path = os.path.join(absolute_path, file_name)
            template: Template = get_template(template_name)
            file = template.render(
                component_name=component_name,
                version=version,
                splight_cli_version=__version__,
            )
            with open(file_path, "w+") as f:
                f.write(file)

    def readme(self, path: str, force: Optional[bool] = False):
        spec_file_path = os.path.join(path, SPEC_FILE)
        spec = Spec.from_file(spec_file_path)
        name = spec.name
        version = spec.version
        description = spec.description
        if os.path.exists(os.path.join(path, README_FILE)) and not force:
            raise ReadmeExists(path)
        template = get_template("auto_readme.md")
        parsed_bindings = [
            json.loads(binding.json()) for binding in spec.bindings
        ]
        readme = template.render(
            component_name=name,
            version=version,
            description=description,
            component_type=spec.component_type,
            inputs=spec.input,
            custom_types=spec.custom_types,
            bindings=parsed_bindings,
            commands=spec.commands,
            output=spec.output,
            endpoints=spec.endpoints,
        )
        with open(os.path.join(path, README_FILE), "w+") as f:
            f.write(readme)
        console.print(f"{README_FILE} created for {name} {version}")

    def install_requirements(self, path: str):
        loader = InitLoader(path=path)
        loader.load()

    def run(
        self,
        path: str,
        component_id: str,
        local_environment: bool = False,
    ):
        spec = Spec.from_file(os.path.join(path, SPEC_FILE))
        self._validate_cli_version(spec.splight_cli_version)
        component_cmd = self._generate_command("python", component_id)
        component_path = Path(path).resolve()
        environment = os.environ.copy()
        environment.update({"LOCAL_ENVIRONMENT": f"{local_environment}"})
        output = subprocess.run(
            component_cmd,
            capture_output=False,
            check=True,
            shell=False,
            cwd=component_path,
            env=environment,
        )
        if output.returncode != 0:
            raise ComponentExecutionError("Error during component execution")

    def _generate_command(
        self, language: AvailableLanguages, component_id: str
    ) -> List[str]:
        cmd = BASE_COMMANDS[language]
        cmd.extend(["--component-id", f"{component_id}"])
        return cmd

    def _validate_cli_version(self, component_cli_version: str):
        if component_cli_version != __version__:
            raise InvalidSplightCLIVersion(component_cli_version, __version__)

    #
    # def test(
    #     self,
    #     path: str,
    #     name: Optional[str] = None,
    #     debug: bool = False,
    # ):
    #     abs_path = str(Path(path).resolve())
    #     if not os.path.exists(abs_path):
    #         console.print(
    #             "Error: test file passed as argument does not exists"
    #         )
    #         raise ComponentTestFileDoesNotExists(TESTS_FILE)
    #
    #     # Add path to environ, used in component fixture tests
    #     os.environ["COMPONENT_PATH_FOR_TESTING"] = abs_path
    #     test_path = os.path.join(abs_path, TESTS_FILE)
    #     cmd = " ".join([TEST_CMD, test_path])
    #
    #     if name:
    #         cmd = "::".join([cmd, name])
    #
    #     if debug:
    #         cmd = " ".join([cmd, "-s"])
    #
    #     r = run(cmd, shell=True, check=True)
    #     stdout, stderr, returncode = r.stdout, r.stderr, r.returncode
    #
    #     if returncode != 0:
    #         if stderr:
    #             console.print(stderr)
    #         raise ComponentTestError
    #     if stdout:
    #         console.print(stdout.decode())
