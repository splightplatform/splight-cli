import json
import os
import shutil
from typing import Optional

import pathspec
import py7zr
from cli.component.component import ComponentManager
from cli.constants import (
    COMPRESSION_TYPE,
    PYTHON_TESTS_FILE,
    SPEC_FILE,
    SPLIGHT_IGNORE,
    success_style,
)
from cli.hub.component.exceptions import (
    ComponentAlreadyExists,
    ComponentDirectoryAlreadyExists,
    ComponentPullError,
    ComponentPushError,
    HubComponentNotFound,
)
from cli.utils.loader import Loader
from rich.console import Console
from rich.table import Table
from splight_lib.models import HubComponent, HubComponentVersion

console = Console()


class HubComponentManager:
    def push(self, path: str, force: Optional[bool] = False):
        with open(os.path.join(path, SPEC_FILE)) as fid:
            spec = json.load(fid)

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
            component = self._upload_component(path, name, version)

        console.print(
            f"Component {component.id} pushed succesfully", style=success_style
        )

    def pull(self, name: str, version: str):
        with Loader("Pulling component from Splight Hub"):
            self._pull_component(name, version)

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
            raise ComponentPullError(name, version) from exc
        finally:
            if os.path.exists(file_name):
                os.remove(file_name)

    def list_components(self):
        components = HubComponent.list_mine()
        table = Table("Name")
        for item in components:
            table.add_row(item.name)
        console.print(table)

    def versions(self, name: str):
        components = HubComponentVersion.list_mine(name=name)
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

    def _upload_component(
        self, path: str, name: str, version: str
    ) -> HubComponent:
        try:
            component = HubComponent.upload(path)
        except Exception as exc:
            raise ComponentPushError(name, version) from exc
        return component

    def _get_component(self, name: str, version: str):
        public = HubComponent.list_public(name=name, version=version)
        private = HubComponent.list_private(name=name, version=version)
        return list(public) + list(private)

    def _exists_in_hub(self, name: str, version: str) -> bool:
        components = self._get_component(name, version)
        return len(components) > 0

    def fetch_component_version(self, name: str, version: str):
        components = self._get_component(name, version)
        if not components:
            raise HubComponentNotFound(name, version)
        return components[0]
