import os
import subprocess
from typing import List, Union

from splight_lib.logging._internal import get_splight_logger

from splight_cli.constants import INIT_FILE

logger = get_splight_logger()
Primitive = Union[int, str, float, bool]


class InitLoader:
    def __init__(self, path: str) -> None:
        self.path = path
        self._validate()

    def _handle_RUN(self, command: List[str]) -> None:
        command: str = " ".join(command)
        logger.debug(f"Running initialization command: {command} ...")
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

    def load(self):
        commands = self._load_commands()
        for command in commands:
            prefix: str = command[0]
            handler = getattr(self, f"_handle_{prefix}", None)
            if not handler:
                raise Exception(f"Invalid command: {prefix}")
            handler(command[1:])

    def _validate(self):
        # VALIDATE FILES
        if not os.path.isfile(os.path.join(self.path, INIT_FILE)):
            raise Exception(f"{INIT_FILE} file is missing in {self.path}")
