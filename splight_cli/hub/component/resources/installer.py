import argparse
import os
import subprocess
from typing import List


class HubComponentInstaller:
    _INIT_FILE = "Initialization"

    def __init__(self, name: str, version: str) -> None:
        self._name = name
        self._version = version
        self._component_path = os.getenv("APP_DIR", "/app")

    def _handle_run(self, command: List[str]) -> None:
        command: str = " ".join(command)
        try:
            subprocess.run(
                command, check=True, cwd=self._component_path, shell=True
            )
        except subprocess.CalledProcessError as e:
            raise Exception(
                f"Failed to run command: {e.cmd}. Output: {e.output}"
            )

    def _validate(self):
        # VALIDATE INIT FILE EXISTS
        if not os.path.isfile(
            os.path.join(self._component_path, self._INIT_FILE)
        ):
            raise Exception(
                f"{self._INIT_FILE} file is missing in {self._component_path}"
            )

    def _load_commands(self) -> List[List[str]]:
        file = os.path.join(self._component_path, self._INIT_FILE)
        lines: List[List[str]] = []
        lines.append(["RUN", "pip", "cache", "purge"])
        with open(file) as f:
            for line in f:
                line = line.strip()
                if line.startswith("#") or line == "":
                    continue
                lines.append(line.split(" "))
        return lines

    def install(self):
        self._validate()
        commands = self._load_commands()
        for command in commands:
            prefix: str = command[0].lower()
            handler = getattr(self, f"_handle_{prefix}", None)
            if not handler:
                raise Exception(f"Invalid command: {prefix}")
            handler(command[1:])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Install Hub Component")
    parser.add_argument(
        "-n",
        "--name",
        type=str,
        nargs=1,
        help="Hub Component Name",
        required=True,
    )
    parser.add_argument(
        "-v",
        "--version",
        type=str,
        nargs=1,
        help="Hub Component Version",
        required=True,
    )

    args = parser.parse_args()

    manager = HubComponentInstaller(name=args.name[0], version=args.version[0])
    manager.install()
