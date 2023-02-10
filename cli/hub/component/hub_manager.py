import json
import os
import shutil
from typing import Any, Dict, Optional

import py7zr
from rich.console import Console
from rich.table import Table
from splight_abstract.hub import AbstractHubClient
from splight_models import HubComponent, HubComponentVersion
from splight_models.constants import ComponentType

from cli.constants import (
    COMPRESSION_TYPE,
    README_FILE,
    SPEC_FILE,
    success_style,
)
from cli.hub.component.exceptions import (
    ComponentAlreadyExists,
    ComponentPullError,
    ComponentPushError,
    ComponentDirectoryAlreadyExists,
)
from cli.utils.loader import Loader

console = Console()


class HubComponentManager:
    def __init__(self, client: AbstractHubClient):
        self._client = client

    def push(self, path: str, force: Optional[bool] = False):
        with open(os.path.join(path, SPEC_FILE)) as fid:
            spec = json.load(fid)

        name = spec["name"]
        version = spec["version"]

        if not force and self._exists_in_hub(name, version):
            raise ComponentAlreadyExists(name, version)

        with Loader("Pushing Component to Splight Hub"):
            self._upload_component(spec, path)

        console.print("Component pushed succesfully", style=success_style)

    def pull(self, name: str, version: str):
        with Loader("Pulling component from Splight Hub"):
            response = self._client.download(
                data={"name": name, "version": version}
            )

            component_path = f"{name}/{version}"
            versioned_name = f"{name}-{version}"
            file_name = f"{versioned_name}.{COMPRESSION_TYPE}"
            if os.path.exists(component_path):
                raise ComponentDirectoryAlreadyExists(component_path)

            try:
                with open(file_name, "wb") as fid:
                    fid.write(response[0])

                with py7zr.SevenZipFile(file_name, "r") as z:
                    z.extractall(path=".")
                shutil.move(f"{versioned_name}", component_path)
            except Exception as exc:
                raise ComponentPullError(name, version) from exc
            finally:
                if os.path.exists(file_name):
                    os.remove(file_name)

    def list_components(self):
        components = self._client.mine.get(HubComponent)
        table = Table("Name")
        for item in components:
            table.add_row(item.name)
        console.print(table)

    def versions(self, name: str):
        components = self._client.mine.get(HubComponentVersion, name=name)

        table = Table("Name", "Version", "Verification", "Privacy Policy")
        for item in components:
            table.add_row(
                name, item.version, item.verification, item.privacy_policy
            )
        console.print(table)

    def _upload_component(self, spec: Dict[str, Any], path: str):
        name = spec["name"]
        version = spec["version"]

        file_name = f"{name}-{version}.{COMPRESSION_TYPE}"
        versioned_name = f"{name}-{version}"
        readme_path = os.path.join(path, README_FILE)
        try:
            with py7zr.SevenZipFile(file_name, "w") as fid:
                fid.writeall(path, versioned_name)

            data = {
                "name": name,
                "version": version,
                "splight_cli_version": spec["splight_cli_version"],
                "privacy_policy": spec.get("privacy_policy", "private"),
                "tags": spec.get("tags", []),
                "component_type": spec.get("component_type", "algorithm"),
                "custom_types": json.dumps(spec.get("custom_types", [])),
                "input": json.dumps(spec.get("input", [])),
                "output": json.dumps(spec.get("output", [])),
                "component_type": spec.get("component_type", ComponentType.CONNECTOR.value),
                "commands": json.dumps(spec.get("commands", [])),
                "bindings": json.dumps(spec.get("bindings", [])),
                "endpoints": json.dumps(spec.get("endpoints", [])),
            }
            files = {
                "file": open(file_name, "rb"),
                "readme": open(readme_path, "rb"),
            }
            self._client.upload(
                data=data,
                files=files,
            )
        except Exception as exc:
            raise ComponentPushError(name, version) from exc
        finally:
            if os.path.exists(file_name):
                os.remove(file_name)

    def _exists_in_hub(self, name: str, version: str) -> bool:
        exists = False

        public = self._client.public.get(
            HubComponent, name=name, version=version
        )
        private = self._client.private.get(
            HubComponent, name=name, version=version
        )
        if any([list(public), list(private)]):
            exists = True
        return exists
