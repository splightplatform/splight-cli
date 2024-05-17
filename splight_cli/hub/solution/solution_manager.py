import os
from collections import namedtuple
from typing import List

from rich.console import Console
from rich.table import Table
from splight_lib.models import HubSolution

from splight_cli.hub.solution.constants import (
    MAIN_FILE,
    README_FILE,
    VALUES_FILE,
    VARIABLES_FILE,
)
from splight_cli.hub.solution.exceptions import (
    HubSolutionAlreadyExists,
    HubSolutionNotFound,
    MissingSolutionFile,
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
        name: str,
        version: str,
        description: str,
        tags: List[str] = [],
        path: str = ".",
        force: bool = False,
    ):
        try:
            solution = self._get_component(name, version)
        except HubSolutionNotFound:
            exist_in_hub = False
            solution = HubSolution(
                name=name, version=version, description=description, tags=tags
            )
        else:
            exist_in_hub = True

        if not force and exist_in_hub:
            raise HubSolutionAlreadyExists(name, version)

        self._set_files_from_path(solution, path)

        with Loader("Pushing Solution to Splight Hub"):
            solution.save()

    def _set_files_from_path(self, solution: HubSolution, path: str):
        main_file_path = os.path.join(path, MAIN_FILE)
        if os.path.exists(main_file_path):
            solution.main_file = main_file_path
        else:
            raise MissingSolutionFile(MAIN_FILE, path)

        variables_file_path = os.path.join(path, VARIABLES_FILE)
        if os.path.exists(variables_file_path):
            solution.variables_file = variables_file_path
        else:
            raise MissingSolutionFile(VARIABLES_FILE, path)

        values_file_path = os.path.join(path, VALUES_FILE)
        if os.path.exists(values_file_path):
            solution.values_file = values_file_path
        else:
            raise MissingSolutionFile(VALUES_FILE, path)

        readme_file_path = os.path.join(path, README_FILE)
        if os.path.exists(readme_file_path):
            solution.readme_file = readme_file_path
        else:
            raise MissingSolutionFile(README_FILE, path)

    def _get_component(self, name: str, version: str) -> HubSolution:
        solutions = HubSolution.list(name=name, version=version)
        if not solutions:
            raise HubSolutionNotFound(name, version)
        return solutions[0]
