import json
import os
from pathlib import Path
from subprocess import run
from typing import Dict, List, Optional

from cli.component.exceptions import (
    ComponentTestError,
    ComponentTestFileDoesNotExists,
    InvalidSplightCLIVersion,
    ReadmeExists,
)
from cli.component.loaders import ComponentLoader, InitLoader, SpecLoader
from cli.component.spec import Spec
from cli.constants import (
    COMPONENT_FILE,
    README_FILE_1,
    SPLIGHT_IGNORE,
    TEST_CMD,
    TESTS_FILE,
)
from cli.utils import get_template, input_single
from cli.version import __version__
from jinja2 import Template
from rich.console import Console
from splight_lib.execution import Thread
from splight_models import Component as ComponentModel

console = Console()


class Component:
    name = None
    version = None

    def __init__(self, context):
        self.context = context

    def create(
        self, name: str, version: str = "0.1.0", component_path: str = "."
    ):
        Spec.verify(
            {
                "name": name,
                "version": version,
                "splight_cli_version": __version__,
                "custom_types": [],
                "input": [],
                "output": [],
                "endpoints": [],
            }
        )

        absolute_path = os.path.abspath(component_path)
        if not os.path.exists(absolute_path):
            os.makedirs(absolute_path)

        files_to_create = ComponentLoader.REQUIRED_FILES
        files_to_create.append(SPLIGHT_IGNORE)
        files_to_create.append(TESTS_FILE)

        for file_name in files_to_create:
            template_name = file_name
            file_path = os.path.join(absolute_path, file_name)
            if file_name == COMPONENT_FILE:
                template_name = "component.py"
            template: Template = get_template(template_name)
            file = template.render(
                component_name=name,
                version=version,
                splight_cli_version=__version__,
            )
            with open(file_path, "w+") as f:
                f.write(file)

    def run(
        self,
        path: str,
        input_parameters: Optional[List[Dict]] = None,
        component_id: Optional[str] = None,
    ):
        # Load py module and validate Splight Component structure
        loader = ComponentLoader(path=path)
        component_class = loader.load()
        # Load json and validate Spec structure
        loader = SpecLoader(path=path)

        if component_id and not input_parameters:
            remote_input_parameters = []
            db_client = self.context.framework.setup.DATABASE_CLIENT(
                namespace="default", path=path
            )
            component_input = db_client.get(
                ComponentModel, id=component_id, first=True
            ).input

            for input in component_input:
                remote_input_parameters.append(input.__dict__)

            input_parameters = remote_input_parameters

        run_spec = loader.load(input_parameters=input_parameters)
        self._validate_cli_version(run_spec.splight_cli_version)
        component = component_class(
            run_spec=run_spec.dict(),
            initial_setup=self.context.workspace.settings.dict(),
            component_id=component_id,
            database_config={"path": path},
            datalake_config={"path": path},
        )
        component.execution_client.start(Thread(target=component.start))

    def install_requirements(self, path: str):
        loader = InitLoader(path=path)
        loader.load()

    def _validate_cli_version(self, component_cli_version: str):
        if component_cli_version != __version__:
            raise InvalidSplightCLIVersion(component_cli_version, __version__)

    def readme(self, path: str, force: Optional[bool] = False):
        loader = SpecLoader(path=path)
        spec = loader.load(prompt_input=False)
        name = spec.name
        version = spec.version
        description = spec.description
        if os.path.exists(os.path.join(path, README_FILE_1)):
            if not force:
                raise ReadmeExists(path)
            else:
                os.remove(os.path.join(path, README_FILE_1))
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
        with open(os.path.join(path, README_FILE_1), "w+") as f:
            f.write(readme)
        console.print(f"{README_FILE_1} created for {name} {version}")

    def test(
        self,
        path: str,
        name: Optional[str] = None,
        debug: bool = False,
    ):
        abs_path = str(Path(path).resolve())
        if not os.path.exists(abs_path):
            console.print(
                "Error: test file passed as argument does not exists"
            )
            raise ComponentTestFileDoesNotExists(TESTS_FILE)

        # Add path to environ, used in component fixture tests
        os.environ["COMPONENT_PATH_FOR_TESTING"] = abs_path
        test_path = os.path.join(abs_path, TESTS_FILE)
        cmd = " ".join([TEST_CMD, test_path])

        if name:
            cmd = "::".join([cmd, name])

        if debug:
            cmd = " ".join([cmd, "-s"])

        r = run(cmd, shell=True, check=True)
        stdout, stderr, returncode = r.stdout, r.stderr, r.returncode

        if returncode != 0:
            if stderr:
                console.print(stderr)
            raise ComponentTestError
        if stdout:
            console.print(stdout.decode())
