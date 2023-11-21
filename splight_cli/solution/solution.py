from pathlib import Path
from typing import List, Optional, Tuple
from uuid import UUID

import typer
from pydantic import ValidationError
from rich.console import Console
from splight_lib.models import Asset, Component, File, RoutineObject

from splight_cli.solution.apply_exec import ApplyExecutor
from splight_cli.solution.destroyer import Destroyer
from splight_cli.solution.importer import ImporterExecutor
from splight_cli.solution.models import (
    ElementType,
    PlanSolution,
    StateSolution,
)
from splight_cli.solution.plan_exec import PlanExecutor
from splight_cli.solution.replacer import Replacer
from splight_cli.solution.solution_checker import CheckResult, SolutionChecker
from splight_cli.solution.utils import (
    DEFAULT_STATE_PATH,
    PRINT_STYLE,
    bprint,
    confirm_or_yes,
    load_yaml,
    save_yaml,
    to_dict,
)

console = Console()


class SolutionManager:
    def __init__(
        self,
        plan_path: str,
        state_path: Optional[str],
        yes_to_all: bool = False,
    ):
        self._yes_to_all = yes_to_all
        self._plan_path = Path(plan_path)
        self._state_path = Path(state_path) if state_path else None

        self._plan = PlanSolution.model_validate(load_yaml(plan_path))
        self._state = self._get_state()

        self._regex_map = {
            Component.__name__: [
                r"root\['routines'\]",
                r"root\['deployment_capacity'\]",
                r"root\['deployment_type'\]",
            ],
            RoutineObject.__name__: [
                r"root\['config'\]\[\d+\]\['description'\]",
                r"root\['input'\]\[\d+\]\['description'\]",
                r"root\['output'\]\[\d+\]\['description'\]",
            ],
            File.__name__: [
                r"root\['metadata'\]",
                r"root\['url'\]",
            ],
        }
        self._replacer = Replacer(self._state)
        self._solution_checker = SolutionChecker(self._plan, self._state)
        self._import_exec = ImporterExecutor(self._plan, self._state)
        self._plan_exec = PlanExecutor(
            self._state, regex_to_exclude=self._regex_map
        )
        self._apply_exec = ApplyExecutor(
            self._state, self._yes_to_all, regex_to_exclude=self._regex_map
        )
        self._destroyer = Destroyer(self._state, self._yes_to_all)

    def apply(self):
        console.print("\nStarting apply...", style=PRINT_STYLE)
        check_result = self._solution_checker.check()
        self._plan, self._state = check_result.plan, check_result.state
        self._delete_assets_and_components(check_result)
        self._apply_assets_state()
        self._apply_files_state()
        self._replacer.build_reference_map()
        self._apply_components_state()

    def plan(self):
        console.print("\nStarting plan...", style=PRINT_STYLE)
        check_result = self._solution_checker.check()
        self._plan, self._state = check_result.plan, check_result.state
        self._plan_exec.plan_elements_to_delete(check_result)
        self._plan_assets_state()
        self._plan_files_state()
        self._replacer.build_reference_map()
        self._plan_components_state()

    def import_element(self, element: ElementType, id: UUID):
        """Imports an element and saves it to both the plan and state file.

        Parameters
        ----------
        element : ElementType
            A string which is either 'asset' or 'component'.
        id : UUID
            The UUID of the element we want to import.
        """
        result = self._import_exec.import_element(element, id)
        if result.was_imported:
            self._plan, self._state = result.plan, result.state
            save_yaml(self._plan_path, self._plan)
            save_yaml(self._state_path, self._state)

    def destroy(self):
        console.print("\nStarting destroy...", style=PRINT_STYLE)
        console.print(
            "WARNING: You are about to destroy every asset and component "
            "defined in the plan. Imported assets and components won't be "
            "destroyed.",
            style="bold red",
        )
        state_assets = self._state.assets
        for idx in range(len(state_assets) - 1, -1, -1):
            asset_to_delete = state_assets[idx]
            destroyed = self._destroyer.destroy(Asset, asset_to_delete)
            if destroyed:
                state_assets.pop(idx)
                save_yaml(self._state_path, self._state)

        state_components = self._state.components
        for idx in range(len(state_components) - 1, -1, -1):
            component_to_delete = state_components[idx]
            destroyed = self._destroyer.destroy(Component, component_to_delete)
            if destroyed:
                state_components.pop(idx)
                save_yaml(self._state_path, self._state)

        state_files = self._state.files
        for idx in range(len(state_files) - 1, -1, -1):
            file_to_delete = state_files[idx]
            destroyed = self._destroyer.destroy(File, file_to_delete)
            if destroyed:
                state_files.pop(idx)
                save_yaml(self._state_path, self._state)

    def _get_state(self):
        """Returns the state file."""
        if self._state_path is not None:
            try:
                return StateSolution.model_validate(
                    load_yaml(self._state_path)
                )
            except ValidationError:
                pass
        else:
            self._state_path = self._plan_path.parent / DEFAULT_STATE_PATH

        state = StateSolution.model_validate(to_dict(self._plan))
        bprint(
            "No state file was passed hence the following state file was "
            "generated from the plan."
        )
        bprint(state)
        bprint(f"The state file will be saved to {self._state_path}")
        confirm = confirm_or_yes(self._yes_to_all, "Do you want to save it?")
        if confirm:
            save_yaml(self._state_path, state)
        else:
            raise typer.Abort("Cannot continue without a state file.")
        return state

    def _plan_assets_state(self):
        """Shows the assets state if the plan were to be applied."""
        assets_list = self._state.assets + self._state.imported_assets
        for state_asset in assets_list:
            self._plan_exec.plan_elem_state(Asset, state_asset)

    def _plan_components_state(self):
        """Shows the components state if the plan were to be applied."""
        self._replacer.replace_references()
        components_list = (
            self._state.components + self._state.imported_components
        )
        for state_component in components_list:
            self._plan_exec.plan_elem_state(Component, state_component)
            self._plan_routines_state(state_component)

    def _plan_routines_state(self, component: Component):
        """Shows the routines state if the plan were to be applied."""
        for routine in component.routines:
            self._plan_exec.plan_elem_state(RoutineObject, routine)

    def _plan_files_state(self):
        """Shows the files state if the plan were to be applied."""
        files_list = self._state.files
        for state_file in files_list:
            self._plan_exec.plan_elem_state(File, state_file)

    def _delete_assets_and_components(self, check_result: CheckResult):
        """Deletes assets and/or components that have been removed from the
        plan.

        Parameters
        ----------
        check_result : CheckResult
            The solution checker results.
        """
        for asset in check_result.assets_to_delete:
            self._apply_exec.delete(Asset, asset)
            save_yaml(self._state_path, self._state)

        for component in check_result.components_to_delete:
            self._apply_exec.delete(Component, component)
            save_yaml(self._state_path, self._state)

    def _apply_assets_state(self):
        """Applies Assets states to the engine."""
        assets_list = self._state.assets
        for i in range(len(assets_list)):
            result = self._apply_exec.apply(
                model=Asset, local_instance=assets_list[i]
            )
            if result.update:
                assets_list[i] = Asset.model_validate(result.updated_dict)
                save_yaml(self._state_path, self._state)

        imported_assets_list = self._state.imported_assets
        for i in range(len(imported_assets_list)):
            result = self._apply_exec.apply(
                model=Asset,
                local_instance=imported_assets_list[i],
                not_found_is_exception=True,
            )
            if result.update:
                imported_assets_list[i] = Asset.model_validate(
                    result.updated_dict
                )
                save_yaml(self._state_path, self._state)

    def _apply_components_state(self):
        """Applies Components states to the engine."""
        self._replacer.replace_references()
        components_list = self._state.components
        for i in range(len(components_list)):
            component = components_list[i]
            result = self._apply_exec.apply(
                model=Component, local_instance=component
            )
            if result.update:
                components_list[i] = Component.model_validate(
                    result.updated_dict
                )
                save_yaml(self._state_path, self._state)
            updated_routines = self._apply_routines_state(
                component, Component.model_validate(result.updated_dict)
            )
            components_list[i].routines = updated_routines
            save_yaml(self._state_path, self._state)

        imported_comp_list = self._state.imported_components
        for i in range(len(imported_comp_list)):
            component = imported_comp_list[i]
            result = self._apply_exec.apply(
                model=Component,
                local_instance=component,
                not_found_is_exception=True,
            )
            if result.update:
                imported_comp_list[i] = Component.model_validate(
                    result.updated_dict
                )
                save_yaml(self._state_path, self._state)
            updated_routines = self._apply_routines_state(
                component,
                Component.model_validate(result.updated_dict),
                not_found_is_exception=True,
            )
            imported_comp_list[i].routines = updated_routines
            save_yaml(self._state_path, self._state)

    def _apply_routines_state(
        self,
        component: Component,
        updated_component: Component,
        not_found_is_exception: bool = False,
    ) -> List[RoutineObject]:
        """Applies RoutineObject states to the engine."""
        routine_list = component.routines
        component_id = updated_component.id
        for i in range(len(routine_list)):
            routine_list[i].component_id = component_id
            result = self._apply_exec.apply(
                model=RoutineObject,
                local_instance=routine_list[i],
                not_found_is_exception=not_found_is_exception,
            )
            if result.update:
                routine_list[i] = RoutineObject.model_validate(
                    result.updated_dict
                )
        return routine_list

    def _apply_files_state(self):
        """Applies Files states to the engine."""
        files_list = self._state.files
        for i in range(len(files_list)):
            result = self._apply_exec.apply(
                model=File, local_instance=files_list[i]
            )
            if result.update:
                files_list[i] = File.model_validate(result.updated_dict)
                save_yaml(self._state_path, self._state)
