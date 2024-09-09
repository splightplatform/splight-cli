import json
import os
import shutil
from collections import namedtuple

import py7zr
from pydantic import ValidationError
from rich.console import Console
from rich.table import Table
from splight_lib.models import HubSolution

from splight_cli.constants import COMPRESSION_TYPE, SPEC_FILE, success_style
from splight_cli.hub.exceptions import SpecFormatError, SpecValidationError
from splight_cli.hub.solution.exceptions import (
    HubSolutionAlreadyExists,
    HubSolutionNotFound,
    SolutionDirectoryAlreadyExists,
)
from splight_cli.utils.loader import Loader

console = Console()


class HubSolutionManager:
    def list_solutions(self):
        solution_tuple = namedtuple("Solution", ["name", "version"])
        all_solutions = HubSolution.list()
        solutions = set(
            [
                solution_tuple(solution.name, solution.version)
                for solution in all_solutions
            ]
        )
        table = Table("Name", "Version", title="Hub Solution List")
        [table.add_row(sol.name, sol.version) for sol in solutions]
        console.print(table)

    def push(
        self,
        path: str = ".",
        force: bool = False,
    ):
        try:
            with open(os.path.join(path, SPEC_FILE)) as fid:
                spec = json.load(fid)
        except Exception as exc:
            raise SpecFormatError(exc)

        # Validate spec fields before pushing the model
        try:
            instance = HubSolution.model_validate(spec)
        except ValidationError as exc:
            raise SpecValidationError(exc)

        name = instance.name
        version = instance.version

        if not force and self._exists_in_hub(name, version):
            raise HubSolutionAlreadyExists(name, version)

        with Loader("Pushing Solution to Splight Hub"):
            solution = HubSolution.upload(path)

        console.print(
            f"Solution {solution.id} pushed succesfully", style=success_style
        )

    def pull(self, name: str, version: str):
        with Loader("Pulling solution from Splight Hub"):
            self._pull_solution(name, version)
        console.print(
            f"Solution {name} pulled succesfully", style=success_style
        )

    def _pull_solution(self, name: str, version: str):
        solution = self._get_hub_solution(name, version)
        name, version = solution.name, solution.version
        file_wrapper = solution.download()
        file_data = file_wrapper.read()

        version_modified = version.replace(".", "_")
        solution_path = f"{name}/{version_modified}"
        versioned_name = f"{name}-{version}"
        file_name = f"{versioned_name}.{COMPRESSION_TYPE}"
        if os.path.exists(solution_path):
            raise SolutionDirectoryAlreadyExists(solution_path)

        try:
            with open(file_name, "wb") as fid:
                fid.write(file_data)

            with py7zr.SevenZipFile(file_name, "r") as z:
                z.extractall(path=".")
            shutil.move(f"{versioned_name}", solution_path)
        except Exception as exc:
            raise exc
        finally:
            if os.path.exists(file_name):
                os.remove(file_name)

    def _get_hub_solution(self, name: str, version: str) -> HubSolution:
        solutions = HubSolution.list(name=name, version=version)
        if not solutions:
            raise HubSolutionNotFound(name, version)
        return solutions[0]

    def _exists_in_hub(self, name: str, version: str) -> bool:
        try:
            self._get_hub_solution(name, version)
            return True
        except HubSolutionNotFound:
            return False
