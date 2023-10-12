from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from splight_lib.models import Asset

from cli.solution.apply_exec import ApplyExecutor
from cli.solution.plan_exec import PlanExecutor
from cli.solution.utils import bprint, check_files, load_yaml, save_yaml

console = Console()


class SolutionManager:
    DEFAULT_STATE_PATH = "state.yml"
    PRINT_STYLE = "bold black on white"

    def __init__(
        self, plan_path: str, state_path: Optional[str], apply: bool = False
    ):
        self._apply = apply
        self._plan_path = Path(plan_path)
        self._state_path = state_path

        self._plan = load_yaml(plan_path)
        self._state = (
            load_yaml(self._state_path)
            if self._state_path is not None
            else None
        )
        if self._state is not None:
            check_files(self._plan, self._state)
        self._plan_exec = PlanExecutor(self._state)
        self._apply_exec = ApplyExecutor(self._state)

    def execute(self):
        if self._state is None:
            self._generate_state()
        else:
            console.print("\nStarting plan step...", style=self.PRINT_STYLE)
            self._generate_assets_state()
            # self._generate_components_state()

        if self._apply:
            console.print("\nStarting apply step...", style=self.PRINT_STYLE)
            self._apply_asset_state()
            # self._apply_components_state()

    def _generate_state(self):
        self._state = self._plan.copy()
        # Replace assets in component routines
        bprint(
            "No state file was passed hence the following state file was "
            "generated from the plan."
        )
        bprint(self._state)
        self._state_path = self._plan_path.parent / self.DEFAULT_STATE_PATH
        bprint(f"The state file will be saved to {self._state_path}")
        confirm = typer.confirm("Do you want to save it?")
        if confirm:
            save_yaml(self._state_path, self._state)

    def _generate_assets_state(self):
        bprint("\nGenerating Assets state...")
        assets_list = self._plan["solution"]["assets"]
        for asset_plan in assets_list:
            self._plan_exec.compare_state_asset(asset_plan)

    def _apply_asset_state(self):
        assets_list = self._state["solution"]["assets"]
        for i in range(len(assets_list)):
            result = self._apply_exec.execute(
                model=Asset, local_dict=assets_list[i]
            )
            if result.update:
                assets_list[i].update(result.updated_dict)
                save_yaml(self._state_path, self._state)

    # def _process_components_plan(self):
    #     bprint("\nComparing Components...")
    #     components_list = plan["solution"]["components"]
    #     for component_plan in components_list:
    #         component_state = self._comparison.find_state_component(
    #             component_plan, state
    #         )
    #         if component_state is not None:
    #             self._comparison.compare_dict(
    #                 component_plan, component_state, self._EXCLUDE_ID_REGEX
    #             )
