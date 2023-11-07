from typing import Any, Dict, List, Type, Union

from deepdiff import DeepDiff
from splight_lib.models.component import (
    Asset,
    Component,
    InputDataAddress,
    RoutineObject,
)

from cli.solution.exceptions import UndefinedID
from cli.solution.models import StateSolution
from cli.solution.solution_checker import CheckResult
from cli.solution.utils import (
    MatchResult,
    SplightTypes,
    bprint,
    parse_str_data_addr,
    to_dict,
)


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
        """Shows which elements (assets or component) are going to be removed
        if the plan were to be applied.

        Parameters
        ----------
        check_results : CheckResult
            The result solution checker.
        """
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
        """Shows what is going to happen to a certain Asset if the plan is
        applied.

        Parameters
        ----------
        state_asset : Asset
            The state asset to analyze.
        """
        instance_id = state_asset.id

        if instance_id is not None:
            return self._compare_with_remote(Asset, state_asset)
        bprint(f"The following Asset will be created:")
        bprint(state_asset)

    def plan_component_state(self, state_component: Component):
        """Shows what is going to happen to a certain Component if the plan is
        applied.

        Parameters
        ----------
        state_component : Component
            The state component to analyze.
        """
        instance_id = state_component.id
        if instance_id is not None:
            return self._compare_with_remote(Component, state_component)
        bprint(f"The following Component will be created:")
        bprint(state_component)

    def plan_routine_state(self, state_routine: RoutineObject):
        """Shows what is going to happen to a certain Routine if the plan is
        applied.

        Parameters
        ----------
        state_routine : RoutineObject
            The state routine of a given component to analyze.
        """
        instance_id = state_routine.id
        if instance_id is not None:
            return self._compare_with_remote(RoutineObject, state_routine)
        bprint(f"The following Routine will be created:")
        bprint(state_routine)

    def replace_data_addr(self):
        """Replaces assets data addresses in component's routines if possible."""
        state_components = self._state.components
        for i in range(len(state_components)):
            routines = state_components[i].routines
            component_name = state_components[i].name
            for routine in routines:
                self._replace_routine_data_addr(routine, component_name)

    def _compare_with_remote(
        self, model: Type[SplightTypes], local_instance: SplightTypes
    ):
        """Compares the given local_instance to the remote analogous.

        Parameters
        ----------
        model : Type[SplightTypes]
            A Splight type.
        local_instance : SplightTypes
            The instance to analyze.
        """
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

    def _replace_routine_data_addr(
        self, routine: RoutineObject, component_name: str
    ):
        """Replaces assets data addresses in a routine.

        Parameters
        ----------
        routine : RoutineObject
            The routine where we will replace the data addresses.
        component_name : str
            The component name.
        """
        for io_elem in routine.input + routine.output:
            if io_elem.value is not None:
                io_elem.value = self._get_new_value(
                    io_elem, component_name, routine.name
                )

    def _get_new_value(
        self, io_elem: InputDataAddress, component_name: str, routine_name: str
    ) -> Union[List[Dict], Dict]:
        """Gets the new data address value.

        Parameters
        ----------
        io_elem : InputDataAddress
            Input or output element to replace with the corresponding data
            addresses.
        component_name : str
            The component name.
        routine_name : str
            The routine name.

        Returns
        -------
        Union[List[Dict], Dict]
            Input or output element where data addresses were replaced.

        Raises
        ------
        ValueError
            Raised if passed a multiple: false element and a list value.
        """
        multiple = io_elem.multiple
        if not multiple and isinstance(io_elem.value, list):
            raise ValueError(
                f"Passed 'multiple: False' but value of {io_elem.name} is "
                "a list. Aborted."
            )
        if multiple:
            return [
                self._parse_data_addr(da, component_name, routine_name)
                for da in io_elem.value
            ]
        else:
            return self._parse_data_addr(
                io_elem.value, component_name, routine_name
            )

    def _parse_data_addr(
        self, data_addr: Dict[str, str], component_name: str, routine_name: str
    ) -> Dict[str, str]:
        """Parses a data address ids.

        Parameters
        ----------
        data_addr : Dict[str, str]
            The data address to be parsed.
        component_name : str
            The component name.
        routine_name : str
            The routine name.

        Returns
        -------
        Dict[str, str]
            A dictionary containing the asset and attribute ids.
        """
        result = parse_str_data_addr(data_addr)
        if result.is_id:
            self._check_ids_are_defined(result, component_name, routine_name)
            return {"asset": result.asset, "attribute": result.attribute}
        state_assets = self._state.assets
        for asset in state_assets:
            if asset.name == result.asset:
                asset_id = asset.id
                for attr in asset.attributes:
                    if attr.name == result.attribute:
                        attribute_id = attr.id
                        return {"asset": asset_id, "attribute": attribute_id}
        raise UndefinedID(
            f"The asset: '{result.asset}' attribute: '{result.attribute}' "
            f"used in the routine named '{routine_name}' of the "
            f"component '{component_name}' is not defined in the plan."
        )

    def _check_ids_are_defined(
        self, result: MatchResult, component_name: str, routine_name: str
    ):
        """Checks if an asset id is defined in the state file.

        Parameters
        ----------
        result : ApplyResult
            The result from parsing the asset string.
        component_name : str
            The component name.
        routine_name : str
            The routine name.

        Raises
        ------
        UndefinedID
            raised when the asset is not found in the state file.
        """
        for asset in self._state.assets + self._state.imported_assets:
            if result.asset == asset.id:
                for attr in asset.attributes:
                    if result.attribute == attr.id:
                        return
        raise UndefinedID(
            f"The asset: '{result.asset}' attribute: '{result.attribute}' "
            f"used in the routine named '{routine_name}' of the "
            f"component '{component_name}' is not defined in the plan."
        )
