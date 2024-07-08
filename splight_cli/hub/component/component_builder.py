import gzip
import os
import re
import shutil
import sys

import docker

from splight_cli.hub.component.exceptions import BuildError


class ComponentBuilder:
    _RESOURCES_PATH = "resources"
    _RESOURCES = [
        "Dockerfile",
        "installer.py",
    ]

    def __init__(self, component_spec: dict, component_path: str):
        self._base_path = os.path.dirname(__file__)
        self._component_name = component_spec["name"]
        self._component_version = component_spec["version"]
        self._spl_pkg = (
            "splight-lib"
            if component_spec["splight_lib_version"]
            else "splight-cli"
        )
        self._spl_pkg_version = (
            component_spec["splight_lib_version"]
            if component_spec["splight_lib_version"]
            else component_spec["splight_cli_version"]
        )
        self._component_path = component_path
        self._docker_client = docker.from_env()

    def build(self) -> str:
        original_path = os.getcwd()
        self._copy_resources()
        os.chdir(self._component_path)
        image_file = self._build_component()
        self._clean_up()
        os.chdir(original_path)
        return image_file

    def _build_component(self) -> str:
        full_name = f"{self._component_name}-{self._component_version}"
        tag = f"component:{full_name}"
        streamer = self._build_component_image(tag)
        for chunk in streamer:
            try:
                log = self._parse_chunk(chunk)
            except BuildError as exc:
                sys.stdout.write(exc)
                sys.stdout.flush()
                raise exc
            if log:
                sys.stdout.write(f"{log}\n")
                sys.stdout.flush()

            if "stream" in chunk:
                match = re.search(
                    r"(^Successfully built |sha256:)([0-9a-f]+)$",
                    chunk["stream"],
                )
                if match:
                    image_id = match.group(2)
        image = self._docker_client.images.get(image_id)
        file_name = f"{full_name}.tgz"
        with gzip.open(file_name, "wb") as image_file:
            for chunk in image.save(named=True):
                image_file.write(chunk)
        return file_name

    def _build_component_image(self, tag: str):
        client = self._docker_client.api
        streamer = client.build(
            path=".",
            tag=tag,
            dockerfile="Dockerfile",
            rm=True,
            pull=True,
            quiet=False,
            buildargs={
                "COMPONENT_NAME": self._component_name,
                "COMPONENT_VERSION": self._component_version,
                "SPL_PACKAGE": self._spl_pkg,
                "SPL_PACKAGE_VERSION": self._spl_pkg_version,
            },
            decode=True,
        )
        return streamer

    def _copy_resources(self):
        for resource in self._RESOURCES:
            resource_path = os.path.join(
                self._base_path, self._RESOURCES_PATH, resource
            )
            shutil.copy(resource_path, self._component_path)

    def _clean_up(self):
        for resource in self._RESOURCES:
            os.remove(resource)

    def _parse_chunk(self, chunk: dict) -> str:
        if "errorDetail" in chunk:
            message = chunk["error"]
            raise BuildError(message)
        log = "".join([str(item) for item in chunk.values()])
        return log.strip("\n") if log != "\n" else ""
