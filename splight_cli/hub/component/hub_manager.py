import json
import os
import shutil
from typing import Optional

import pathspec
import py7zr
from pydantic import ValidationError
from rich.console import Console
from rich.table import Table
from splight_lib.models import HubComponent

from splight_cli.component.component import ComponentManager
from splight_cli.constants import (
    COMPRESSION_TYPE,
    PYTHON_TESTS_FILE,
    SPEC_FILE,
    SPLIGHT_IGNORE,
    success_style,
)
from splight_cli.hub.component.exceptions import (
    ComponentAlreadyExists,
    ComponentDirectoryAlreadyExists,
    HubComponentNotFound,
    SpecFormatError,
    SpecValidationError,
)
from splight_cli.utils.loader import Loader

console = Console()


class HubComponentManager:
    def push(self, path: str, force: Optional[bool] = False):
        try:
            with open(os.path.join(path, SPEC_FILE)) as fid:
                spec = json.load(fid)
        except Exception as exc:
            raise SpecFormatError(exc)

        # Validate spec fields before pushing the model
        try:
            HubComponent.model_validate(spec)
        except ValidationError as exc:
            raise SpecValidationError(exc)

        name = spec["name"]
        version = spec["version"]

        if not force and self._exists_in_hub(name, version):
            raise ComponentAlreadyExists(name, version)

        if os.path.exists(os.path.join(path, PYTHON_TESTS_FILE)):
            # run test before push to hub. To run test, ctx isn't needed
            console.print(
                "Testing component before push to hub...", style=success_style
            )
            ComponentManager().test(path)

        with Loader("Pushing Component to Splight Hub"):
            component = HubComponent.upload(path)

        console.print(
            f"Component {component.id} pushed succesfully", style=success_style
        )

    def pull(self, name: str, version: str):
        with Loader("Pulling component from Splight Hub"):
            self._pull_component(name, version)
        console.print(
            f"Component {name} pulled succesfully", style=success_style
        )

    def _pull_component(self, name: str, version: str):
        components = HubComponent.list_mine(name=name, version=version)
        if not components:
            raise HubComponentNotFound(name, version)

        component_data = components[0].download()

        # TODO: search for a better approach
        version_modified = version.replace(".", "_")
        component_path = f"{name}/{version_modified}"
        versioned_name = f"{name}-{version}"
        file_name = f"{versioned_name}.{COMPRESSION_TYPE}"
        if os.path.exists(component_path):
            raise ComponentDirectoryAlreadyExists(component_path)

        try:
            with open(file_name, "wb") as fid:
                fid.write(component_data)

            with py7zr.SevenZipFile(file_name, "r") as z:
                z.extractall(path=".")
            shutil.move(f"{versioned_name}", component_path)

        except Exception as exc:
            raise exc
        finally:
            if os.path.exists(file_name):
                os.remove(file_name)

    def list_components(self):
        components = HubComponent.list_mine(limit_=10000)
        names = set([component.name for component in components])
        table = Table("Name")
        [table.add_row(name) for name in names]
        console.print(table)

    def versions(self, name: str):
        components = HubComponent.list_mine(name=name)
        table = Table("Name", "Version", "Verification", "Privacy Policy")
        for item in components:
            table.add_row(
                name, item.version, item.verification, item.privacy_policy
            )
        console.print(table)

    def _get_ignore_pathspec(self, path):
        try:
            with open(
                os.path.join(path, SPLIGHT_IGNORE), "r"
            ) as splightignore:
                return pathspec.PathSpec.from_lines(
                    "gitwildmatch", splightignore
                )
        except FileNotFoundError:
            return None

    def _get_component(self, name: str, version: str):
        components = HubComponent.list_all(name=name, version=version)
        return components

    def _exists_in_hub(self, name: str, version: str) -> bool:
        components = self._get_component(name, version)
        return len(components) > 0

    def fetch_component_version(self, name: str, version: str):
        components = self._get_component(name, version)
        if not components:
            raise HubComponentNotFound(name, version)
        return components[0]
