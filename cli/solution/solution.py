from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from splight_lib.models import Asset, Component, RoutineObject

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
        self._state_path = Path(state_path) if state_path else None

        self._plan = load_yaml(plan_path)
        self._state = (
            load_yaml(self._state_path)
            if self._state_path is not None
            else self._generate_state_from_plan()
        )
        check_files(self._plan, self._state)
        self._plan_exec = PlanExecutor(self._state)
        self._apply_exec = ApplyExecutor(
            self._state,
            regex_to_exclude={
                Component.__name__: [
                    r"root\['routines'\]",
                    r"root\['deployment_capacity'\]",
                    r"root\['deployment_type'\]",
                ]
            },
        )

    def execute(self):
        console.print("\nStarting plan step...", style=self.PRINT_STYLE)
        self._generate_assets_state()
        self._generate_components_state()

        if self._apply:
            console.print("\nStarting apply step...", style=self.PRINT_STYLE)
            self._apply_assets_state()
            self._apply_components_state()

    def _generate_state_from_plan(self):
        """Generates the state file if not passed."""
        state = self._plan.copy()
        bprint(
            "No state file was passed hence the following state file was "
            "generated from the plan."
        )
        bprint(state)
        self._state_path = self._plan_path.parent / self.DEFAULT_STATE_PATH
        bprint(f"The state file will be saved to {self._state_path}")
        confirm = typer.confirm("Do you want to save it?")
        if confirm:
            save_yaml(self._state_path, state)
        return state

    def _generate_assets_state(self):
        """Compares assets in the state file."""
        assets_list = self._plan["solution"]["assets"]
        for asset_plan in assets_list:
            self._plan_exec.compare_state_asset(asset_plan)

    def _generate_components_state(self):
        """Compares components in the state file."""
        components_list = self._plan["solution"]["components"]
        for component_plan in components_list:
            self._plan_exec.compare_state_component(component_plan)

    def _apply_assets_state(self):
        """Applies Assets states to the engine."""
        assets_list = self._state["solution"]["assets"]
        for i in range(len(assets_list)):
            result = self._apply_exec.apply(
                model=Asset, local_dict=assets_list[i]
            )
            if result.update:
                assets_list[i].update(result.updated_dict)
                save_yaml(self._state_path, self._state)

    def _apply_components_state(self):
        """Applies Components states to the engine."""
        self._apply_exec.replace_data_addr()
        components_list = self._state["solution"]["components"]
        for i in range(len(components_list)):
            component = components_list[i]
            result = self._apply_exec.apply(
                model=Component, local_dict=component
            )
            if result.update:
                updated_routines = self._apply_routines_state(
                    component, result.updated_dict
                )
                components_list[i].update(result.updated_dict)
                components_list[i]["routines"] = updated_routines
                save_yaml(self._state_path, self._state)

    def _apply_routines_state(self, component, updated_component):
        """Applies RoutineObject states to the engine."""
        routine_list = component["routines"]
        component_id = updated_component["id"]
        for i in range(len(routine_list)):
            routine_list[i]["component_id"] = component_id
            result = self._apply_exec.apply(
                model=RoutineObject, local_dict=routine_list[i]
            )
            if result.update:
                routine_list[i].update(result.updated_dict)
        return routine_list
