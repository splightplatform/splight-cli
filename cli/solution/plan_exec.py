from typing import Any, Dict

from deepdiff import DeepDiff
from splight_lib.models.component import (
    Asset,
    Component,
    InputDataAddress,
    RoutineObject,
)

from cli.solution.models import StateSolution
from cli.solution.solution_checker import CheckResult
from cli.solution.utils import bprint, parse_str_data_addr, to_dict


class MissingDataAddress(Exception):
    ...


class PlanExecutor:
    def __init__(self, state: StateSolution, regex_to_exclude: Dict[str, Any]):
        self._state = state

        self._model_to_regex = regex_to_exclude
        self._possible_asset_attr = set()
        for asset in self._state.assets:
            asset_name = asset.name
            for attr in asset.attributes:
                attr_name = attr.name
                self._possible_asset_attr.add(f"{asset_name}-{attr_name}")

    def plan_elements_to_delete(self, check_results: CheckResult):
        for asset in check_results.assets_to_delete:
            bprint(
                "If the plan is applied the following Asset will be deleted:"
            )
            bprint(asset)
        for component in check_results.components_to_delete:
            bprint(
                "If the plan is applied the following Component will be "
                "deleted:"
            )
            bprint(component)

    def plan_asset_state(self, state_asset: Asset):
        """Finds and compares an asset from the plan with the analogous in the
        state file printing the plan in case it's executed.

        Parameters
        ----------
        """
        instance_id = state_asset.id

        if instance_id is not None:
            return self._compare_with_remote(Asset, state_asset)
        bprint(f"The following Asset will be created:")
        bprint(state_asset)

    def plan_component_state(self, state_component: Component):
        """Finds and compares a Component from the plan with the analogous in
        the state file printing the plan in case it's executed.

        Parameters
        ----------
        plan_commponent : Component
            A Component instance.
        """

        self._check_assets_are_defined(state_component)
        instance_id = state_component.id
        if instance_id is not None:
            return self._compare_with_remote(Component, state_component)
        bprint(f"The following Component will be created:")
        bprint(state_component)

    def plan_routine_state(self, state_routine: Component):
        """Finds and compares a Component from the plan with the analogous in
        the state file printing the plan in case it's executed.

        Parameters
        ----------
        plan_commponent : Component
            A Component instance.
        """
        instance_id = state_routine.id
        if instance_id is not None:
            return self._compare_with_remote(RoutineObject, state_routine)
        bprint(f"The following Component will be created:")
        bprint(state_routine)

    def _compare_with_remote(self, model, local_instance):
        model_name = model.__name__
        instance_id = local_instance.id
        instance_name = local_instance.name

        remote_list = model.list(id__in=instance_id)
        if remote_list:
            remote_instance = remote_list[0]
            exclude_regex = self._model_to_regex.get(model_name, None)
            diff = DeepDiff(
                to_dict(remote_instance),
                to_dict(local_instance),
                exclude_regex_paths=exclude_regex,
            )
            if diff:
                bprint(
                    f"\nThe remote {model_name} named {instance_name} with id "
                    f" {instance_id} has the following differences with the "
                    "local item:"
                )
                bprint(diff)
                return
            bprint(
                f"Nothing to update, the same {model_name} named "
                f"{instance_name} was found remotely as defined locally."
            )
            return
        bprint(
            f"\nThe following {model_name} named {instance_name} was not "
            "found remotely. It will be created if the plan is applied."
        )
        bprint(local_instance)

    def _check_assets_are_defined(self, state_component_found: Component):
        """Checks if the assets of a component routine are defined or not in
        the state file.

        Parameters
        ----------
        state_component_found : Component
            The state component.
        """
        routines = state_component_found.routines
        for routine in routines:
            for io_elem in routine.input + routine.output:
                if io_elem.value is not None:
                    self._is_state_asset_attr(io_elem)

    def _is_state_asset_attr(self, io_elem: InputDataAddress):
        """Raises an exception if an asset is not defined in the state file.

        Parameters
        ----------
        io_elem : InputDataAddress
            Input or output element.

        Raises
        ------
        MissingDataAddress
            Raised when an asset is not defined in the state file.
        """
        multiple = io_elem.multiple
        io_values = io_elem.value if multiple else [io_elem.value]
        for data_addr in io_values:
            result = parse_str_data_addr(data_addr)
            if result.is_id:
                continue
            ids_str = f"{result.asset}-{result.attribute}"
            if ids_str not in self._possible_asset_attr:
                raise MissingDataAddress(
                    f"The asset id: {data_addr['asset']} "
                    f"attribute id: {data_addr['attribute']} is "
                    "not defined in the state file. Aborted."
                )
