import json
import os
import subprocess
from enum import auto
from pathlib import Path
from typing import List, Optional

from caseconverter import pascalcase
from jinja2 import Template
from rich.console import Console
from splight_lib.client.database import LOCAL_DB_FILE
from splight_lib.component.spec import Spec
from strenum import LowercaseStrEnum

from splight_cli.component.exceptions import (
    ComponentTestError,
    ComponentTestFileDoesNotExists,
    InvalidSplightCLIVersion,
    ReadmeExists,
)
from splight_cli.component.loaders import InitLoader
from splight_cli.component.utils import (
    db_from_spec,
    fake_asset,
    fake_attribute,
)
from splight_cli.constants import (
    INIT_FILE,
    PYTHON_CMD,
    PYTHON_COMPONENT_FILE,
    PYTHON_TEST_CMD,
    PYTHON_TESTS_FILE,
    README_FILE,
    SPEC_FILE,
    SPLIGHT_IGNORE,
)
from splight_cli.utils import get_template
from splight_cli.version import __version__

console = Console()


class AvailableLanguages(LowercaseStrEnum):
    PYTHON = auto()


BASE_COMMANDS = {
    AvailableLanguages.PYTHON: [PYTHON_CMD, PYTHON_COMPONENT_FILE]
}
TEST_COMMANDS = {
    AvailableLanguages.PYTHON: [PYTHON_TEST_CMD, PYTHON_TESTS_FILE]
}


class ComponentManager:
    _COMPONENT_REQUIRED_FILES = [
        PYTHON_COMPONENT_FILE,
        INIT_FILE,
        README_FILE,
        SPEC_FILE,
        SPLIGHT_IGNORE,
        PYTHON_TESTS_FILE,
    ]

    def create(
        self, name: str, version: str = "0.1.0", component_path: str = "."
    ):
        """Creates the files needed for a new components.

        Parameters
        ----------
        name: str
            The components names
        version: str
            The version for the component
        component_path: str
            The where to create the files
        """
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
        """Creates a README.md following the information provided in the
        spec.json file.

        Parameters
        ----------
        path: str
            The path to the component.
        force: bool
            Wheter to overwrite an existing readme.

        Raises
        ------
        ReadmeExists thrown when the README.md file already exist and
        force=False
        """
        spec_file_path = os.path.join(path, SPEC_FILE)
        spec = Spec.from_file(spec_file_path)
        name = spec.name
        version = spec.version
        description = spec.description
        if os.path.exists(os.path.join(path, README_FILE)) and not force:
            raise ReadmeExists(path)
        template = get_template("auto_readme.md")

        readme = template.render(
            component_name=name,
            version=version,
            description=description,
            component_type=spec.component_type,
            inputs=spec.input,
            custom_types=spec.custom_types,
            routines=spec.routines,
        )
        with open(os.path.join(path, README_FILE), "w+") as f:
            f.write(readme)
        console.print(f"{README_FILE} created for {name} {version}")

    def install_requirements(self, path: str):
        """Installs the requirements of a component

        Parameters
        -----------
        path: str
            The component's path
        """
        loader = InitLoader(path=path)
        loader.load()

    # TODO: Check if the test command should be removed also
    def test(
        self,
        path: str,
        name: Optional[str] = None,
        debug: bool = False,
    ):
        """Runs component's tests.

        Parameters
        ----------
        path: str
            The component's path
        name: Optional[str]
            The name of the test to be executed
        debug: bool
            Wether to use debug mode for running tests
        """
        abs_path = str(Path(path).resolve())
        if not os.path.exists(abs_path):
            console.print(
                "Error: test file passed as argument does not exists"
            )
            raise ComponentTestFileDoesNotExists(PYTHON_TESTS_FILE)

        environment = os.environ.copy()
        environment.update({"LOCAL_ENVIRONMENT": "True"})
        cmd = self._test_command("python", name, debug)
        results = subprocess.run(
            cmd, shell=True, check=True, cwd=abs_path, env=environment
        )
        stdout = results.stdout
        stderr = results.stderr
        returncode = results.returncode

        if returncode != 0:
            if stderr:
                console.print(stderr)
            raise ComponentTestError
        if stdout:
            console.print(stdout.decode())

    def _execution_command(
        self, language: AvailableLanguages, component_id: str
    ) -> List[str]:
        cmd = BASE_COMMANDS[language]
        cmd.extend(["--component-id", f"{component_id}"])
        return cmd

    def _test_command(
        self,
        language: AvailableLanguages,
        name: Optional[str] = None,
        debug: bool = False,
    ) -> str:
        cmd = " ".join(TEST_COMMANDS[language])
        if name:
            cmd = "::".join([cmd, name])
        if debug:
            cmd = " ".join([cmd, "-s"])
        return cmd

    def _validate_cli_version(self, component_cli_version: str):
        if component_cli_version != __version__:
            raise InvalidSplightCLIVersion(component_cli_version, __version__)

    def create_local_db(self, path: str):
        spec = Spec.from_file(os.path.join(path, SPEC_FILE))
        json_spec = spec.model_dump()

        splight_db = db_from_spec(json_spec)

        # agnostic from component
        asset = fake_asset()
        splight_db["asset"].update(asset)

        attribute = fake_attribute()
        splight_db["attribute"].update(attribute)

        with open(LOCAL_DB_FILE, "w") as db_file:
            json.dump(splight_db, db_file, indent=4)
