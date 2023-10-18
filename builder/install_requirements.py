import os
import subprocess
from typing import List

import boto3

# import tarfile
import py7zr

# import logging


# logger = logging.getLogger()

INIT_FILE = "Initialization"


class HubComponentManager:
    def __init__(self, name: str, version: str) -> None:
        self.path = "Sum-1.1.5"
        # print(os.listdir())
        # self._validate()

    def _handle_RUN(self, command: List[str]) -> None:
        command: str = " ".join(command)
        # logger.debug(f"Running initialization command: {command} ...")
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
                #                 raise Exception(f"Invalid command: {prefix}")
                print(f"Invalid command: {prefix}")
            handler(command[1:])

    def download_component(self):
        print("Downloading...")
        filename = "asdfasdf.7z"

        s3_client = boto3.client("s3")
        s3_client.download_file(
            Bucket="integration-splight-api-storage",
            Key="component_files/97f71a89-b42e-4ecb-b02a-51965d974d44/Sum-1.1.5.7z",
            Filename=filename,
        )

        with py7zr.SevenZipFile(filename, "r") as z:
            z.extractall(path=".")

        print("\n\n\n")
        print(os.listdir())
        print("\n\n\n")

    def _validate(self):
        # VALIDATE FILES
        if not os.path.isfile(os.path.join(self.path, INIT_FILE)):
            raise Exception(f"{INIT_FILE} file is missing in {self.path}")
