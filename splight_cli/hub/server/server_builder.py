import gzip
import os
import re
import sys

import docker

from splight_cli.hub.server.exceptions import BuildError


class ServerBuilder:
    def __init__(self, server_spec: dict, server_path: str):
        self._base_path = os.path.dirname(__file__)
        self._server_name = server_spec["name"]
        self._server_version = server_spec["version"]
        self._server_path = server_path
        self._docker_client = docker.from_env()

    def build(self) -> str:
        original_path = os.getcwd()
        os.chdir(self._server_path)
        image_file = self._build_server()
        os.chdir(original_path)
        return image_file

    def _build_server(self) -> str:
        full_name = f"{self._server_name}-{self._server_version}"
        tag = f"server:{full_name}"
        streamer = self._build_server_image(tag)
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

    def _build_server_image(self, tag: str):
        client = self._docker_client.api
        streamer = client.build(
            path=".",
            tag=tag,
            dockerfile="Dockerfile",
            rm=True,
            pull=True,
            quiet=False,
            decode=True,
        )
        return streamer

    def _parse_chunk(self, chunk: dict) -> str:
        if "errorDetail" in chunk:
            message = chunk["error"]
            raise BuildError(message)
        log = "".join([str(item) for item in chunk.values()])
        return log.strip("\n") if log != "\n" else ""
