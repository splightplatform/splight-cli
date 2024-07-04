import sys
import os
import shutil

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

    def build(self):
        original_path = os.getcwd()
        self._copy_resources()
        os.chdir(self._component_path)
        self._build_component()
        self._clean_up()
        os.chdir(original_path)

    def _build_component(self):
        tag = f"component:{self._component_name}-{self._component_version}"
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
        __import__('ipdb').set_trace()

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
