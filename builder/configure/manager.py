import os
import subprocess
from typing import List

import boto3
import py7zr
from settings import s3_settings

INIT_FILE = "Initialization"


class HubComponentManager:
    def __init__(self, spec) -> None:
        self.name = spec["name"]
        self.version = spec["version"]
        self.hub_component_id = spec["id"]

    @property
    def boto3_key(self):
        return f"component_files/{self.hub_component_id}/{self.name}-{self.version}.7z"

    @property
    def zip_filename(self):
        return f"{self.name}-{self.version}.7z"

    @property
    def path(self):
        return f"{self.name}-{self.version}"

    def _handle_RUN(self, command: List[str]) -> None:
        command: str = " ".join(command)
        try:
            subprocess.run(command, check=True, cwd=self.path, shell=True)
        except subprocess.CalledProcessError as e:
            raise Exception(
                f"Failed to run command: {e.cmd}. Output: {e.output}"
            )

    def _load_commands(self) -> List[List[str]]:
        file = os.path.join(self.path, INIT_FILE)
        lines: List[str] = []
        lines.append(["RUN", "pip", "cache", "purge"])
        with open(file) as f:
            for line in f:
                line = line.strip()
                if line.startswith("#") or line == "":
                    continue
                lines.append(line.split(" "))
        return lines

    def install_requirements(self):
        self._validate()
        commands = self._load_commands()
        for command in commands:
            prefix: str = command[0]
            handler = getattr(self, f"_handle_{prefix}", None)
            if not handler:
                raise Exception(f"Invalid command: {prefix}")
            handler(command[1:])

    def download_component(self):
        s3_client = boto3.client("s3")
        s3_client.download_file(
            Bucket=s3_settings.S3_BUCKET_NAME,
            Key=self.boto3_key,
            Filename=self.zip_filename,
        )

        with py7zr.SevenZipFile(self.zip_filename, "r") as z:
            z.extractall(path=".")

    def _validate(self):
        # VALIDATE INIT FILE EXISTS
        if not os.path.isfile(os.path.join(self.path, INIT_FILE)):
            raise Exception(f"{INIT_FILE} file is missing in {self.path}")
