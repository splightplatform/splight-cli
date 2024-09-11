import json
import os
import shutil
from collections import namedtuple
from typing import Optional

import py7zr
from pydantic import ValidationError
from rich.console import Console
from rich.table import Table
from splight_lib.models import HubServer

from splight_cli.constants import COMPRESSION_TYPE, SPEC_FILE, success_style
from splight_cli.hub.exceptions import SpecFormatError, SpecValidationError
from splight_cli.hub.server.exceptions import (
    HubServerNotFound,
    ServerAlreadyExists,
    ServerDirectoryAlreadyExists,
)
from splight_cli.hub.server.server_builder import ServerBuilder
from splight_cli.utils.loader import Loader

console = Console()


class HubServerManager:
    def push(self, path: str, force: Optional[bool] = False):
        try:
            with open(os.path.join(path, SPEC_FILE)) as fid:
                spec = json.load(fid)
        except Exception as exc:
            raise SpecFormatError(exc)

        # Validate spec fields before pushing the model
        try:
            server = HubServer.model_validate(spec)
        except ValidationError as exc:
            raise SpecValidationError(exc)

        name = spec["name"]
        version = spec["version"]

        if not force and self._exists_in_hub(name, version):
            raise ServerAlreadyExists(name, version)

        builder = ServerBuilder(spec, path)
        image_file = builder.build()

        with Loader("Pushing Server to Splight Hub"):
            server = HubServer.upload(path, image_file)

        if image_file:
            os.remove(image_file)

        console.print(
            f"Server {server.id} pushed succesfully", style=success_style
        )

    def pull(self, name: str, version: str):
        with Loader("Pulling server from Splight Hub"):
            self._pull_server(name, version)
        console.print(f"Server {name} pulled succesfully", style=success_style)

    def _pull_server(self, name: str, version: str):
        server = self._get_hub_server(name, version)
        name, version = server.name, server.version

        file_wrapper = server.download()
        file_data = file_wrapper.read()

        version_modified = version.replace(".", "_")
        server_path = f"{name}/{version_modified}"
        versioned_name = f"{name}-{version}"
        file_name = f"{versioned_name}.{COMPRESSION_TYPE}"
        if os.path.exists(server_path):
            raise ServerDirectoryAlreadyExists(server_path)

        try:
            with open(file_name, "wb") as fid:
                fid.write(file_data)

            with py7zr.SevenZipFile(file_name, "r") as z:
                z.extractall(path=".")
            shutil.move(f"{versioned_name}", server_path)

        except Exception as exc:
            raise exc
        finally:
            if os.path.exists(file_name):
                os.remove(file_name)

    def _get_hub_server(self, name: str, version: str) -> HubServer:
        servers = HubServer.list(name=name, version=version)
        if not servers:
            raise HubServerNotFound(name, version)
        return servers[0]

    def list_servers(self):
        servers_tuple = namedtuple("Server", ["name", "version"])
        all_servers = HubServer.list()
        servers = set(
            [
                servers_tuple(server.name, server.version)
                for server in all_servers
            ]
        )
        table = Table("Name", "Version", title="Hub Server List")
        [table.add_row(server.name, server.version) for server in servers]
        console.print(table)

    def _exists_in_hub(self, name: str, version: str) -> bool:
        try:
            self._get_hub_server(name, version)
            return True
        except HubServerNotFound:
            return False
