from pathlib import Path
from typing import List, Optional, Tuple

import typer
from rich.console import Console
from splight_lib.models import Asset, Component, RoutineObject

from cli.solution.apply_exec import ApplyExecutor
from cli.solution.models import Solution
from cli.solution.plan_exec import PlanExecutor
from cli.solution.utils import (
    DEFAULT_STATE_PATH,
    PRINT_STYLE,
    bprint,
    check_files,
    load_yaml,
    save_yaml,
)

console = Console()


class SolutionManager:
    def __init__(
        self, plan_path: str, state_path: Optional[str], apply: bool = False
    ):
        self._apply = apply
        self._plan_path = Path(plan_path)
        self._state_path = Path(state_path) if state_path else None

        self._plan = Solution.parse_obj(load_yaml(plan_path))
        self._state = (
            Solution.parse_obj(load_yaml(self._state_path))
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
        if self._apply:
            console.print("\nStarting apply step...", style=PRINT_STYLE)
            self._apply_assets_state()
            self._apply_components_state()
        else:
            console.print("\nStarting plan step...", style=PRINT_STYLE)
            self._generate_assets_state()
            self._generate_components_state()

    def _generate_state_from_plan(self):
        """Generates the state file if not passed."""
        state = self._plan.copy()
        bprint(
            "No state file was passed hence the following state file was "
            "generated from the plan."
        )
        bprint(state)
        self._state_path = self._plan_path.parent / DEFAULT_STATE_PATH
        bprint(f"The state file will be saved to {self._state_path}")
        confirm = typer.confirm("Do you want to save it?")
        if confirm:
            save_yaml(self._state_path, state)
        return state

    def _generate_assets_state(self):
        """Compares assets in the state file."""
        assets_list = self._plan.assets
        for asset_plan in assets_list:
            self._plan_exec.compare_state_asset(asset_plan)

    def _generate_components_state(self):
        """Compares components in the state file."""
        components_list = self._plan.components
        for component_plan in components_list:
            self._plan_exec.compare_state_component(component_plan)

    def _apply_assets_state(self):
        """Applies Assets states to the engine."""
        assets_list = self._state.assets
        for i in range(len(assets_list)):
            result = self._apply_exec.apply(
                model=Asset, local_instance=assets_list[i]
            )
            if result.update:
                assets_list[i] = Asset.parse_obj(result.updated_dict)
                save_yaml(self._state_path, self._state)

    def _apply_components_state(self):
        """Applies Components states to the engine."""
        self._apply_exec.replace_data_addr()
        components_list = self._state.components
        for i in range(len(components_list)):
            component = components_list[i]
            result = self._apply_exec.apply(
                model=Component, local_instance=component
            )
            if result.update:
                components_list[i] = Component.parse_obj(result.updated_dict)
                save_yaml(self._state_path, self._state)
            updated_routines, was_updated = self._apply_routines_state(
                component, Component.parse_obj(result.updated_dict)
            )
            components_list[i].routines = updated_routines
            if was_updated:
                save_yaml(self._state_path, self._state)

    def _apply_routines_state(
        self, component: Component, updated_component: Component
    ) -> Tuple[List[RoutineObject], bool]:
        """Applies RoutineObject states to the engine."""
        routine_list = component.routines
        component_id = updated_component.id
        update_results = False
        for i in range(len(routine_list)):
            routine_list[i].component_id = component_id
            result = self._apply_exec.apply(
                model=RoutineObject, local_instance=routine_list[i]
            )
            if result.update:
                update_results = True
                routine_list[i] = RoutineObject.parse_obj(result.updated_dict)
        return routine_list, update_results
