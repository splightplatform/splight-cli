from collections import namedtuple
from typing import Any, Dict, List, Union

import typer
from deepdiff import DeepDiff
from rich import print
from splight_lib.models.component import Asset, InputDataAddress, RoutineObject

from cli.solution.models import Solution
from cli.solution.utils import (
    SplightTypes,
    bprint,
    parse_str_data_addr,
    to_dict,
)

ApplyResult = namedtuple("ApplyResult", ("update", "updated_dict"))


class UndefinedID(Exception):
    ...


class ApplyExecutor:
    def __init__(self, state: Solution, regex_to_exclude: Dict[str, Any]):
        self._state = state
        self._model_to_regex = regex_to_exclude

    def apply(
        self, model: SplightTypes, local_instance: SplightTypes
    ) -> ApplyResult:
        """Applies changes to the remote engine if needed.

        Parameters
        ----------
        model : SplightTypes
            A Splight model.
        local_instance : SplightTypes
            Instance to be saved (or not).

        Returns
        -------
        ApplyResult
            Named tuple containing the result of the apply step.
        """
        model_name = model.__name__
        instance_id = local_instance.id

        if instance_id is not None:
            return self._compare_with_remote(model, local_instance)
        bprint(f"You are about to create the following {model_name}:")
        print(local_instance)
        create = typer.confirm("Are you sure?")
        if create:
            local_instance.save()
            remote_instance = model.retrieve(resource_id=local_instance.id)
            return ApplyResult(True, to_dict(remote_instance))
        return ApplyResult(False, to_dict(local_instance))

    def replace_data_addr(self):
        """Replaces assets data addresses in component's routines."""
        state_components = self._state.components
        for i in range(len(state_components)):
            routines = state_components[i].routines
            for routine in routines:
                self._replace_routine_data_addr(routine)

    def _replace_routine_data_addr(self, routine: RoutineObject):
        """Replaces assets data addresses in a routine.

        Parameters
        ----------
        routine : RoutineObject
            The routine where we will replace the data addresses.
        """
        for io_elem in routine.input + routine.output:
            if io_elem.value is not None:
                io_elem.value = self._get_new_value(io_elem)

    def _get_new_value(
        self, io_elem: InputDataAddress
    ) -> Union[List[Dict], Dict]:
        """Gets the new data address value.

        Parameters
        ----------
        io_elem : InputDataAddress
            Input or output element to replace with the corresponding data
            addresses.

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
            return [self._parse_data_addr(da) for da in io_elem.value]
        else:
            return self._parse_data_addr(io_elem.value)

    def _parse_data_addr(self, data_addr: Dict[str, str]) -> Dict[str, str]:
        """Parses a data address ids.

        Parameters
        ----------
        data_addr : Dict[str, str]
            The data address to be parsed.

        Returns
        -------
        Dict[str, str]
            A dictionary containing the asset and attribute ids.
        """
        result = parse_str_data_addr(data_addr)
        if result.is_id:
            self._check_ids_are_defined(result)
            return {"asset": result.asset, "attribute": result.attribute}
        state_assets = self._state.assets
        for asset in state_assets:
            if asset.name == result.asset:
                asset_id = asset.id
                for attr in asset.attributes:
                    if attr.name == result.attribute:
                        attr_id = attr.id
                        break
                break
        return {"asset": asset_id, "attribute": attr_id}

    def _check_ids_are_defined(self, result: ApplyResult):
        """Checks if an asset id is defined in the state file.

        Parameters
        ----------
        result : ApplyResult
            The result from parsing the asset string.

        Raises
        ------
        UndefinedID
            raised when the asset is not found in the state file.
        """
        for asset in self._state.assets:
            if result.asset == asset.id:
                for attr in asset.attributes:
                    if result.attribute == attr.id:
                        return
        raise UndefinedID(
            f"Routine Error: The asset: {result.asset} attribute: "
            f"{result.attribute} is not defined in the state file."
        )

    def _compare_with_remote(
        self, model: SplightTypes, local_instance: SplightTypes
    ) -> ApplyResult:
        """Compares the local instance with the remote instances if any.

        Parameters
        ----------
        model : SplightTypes
            A Splight model.
        local_dict : SplightTypes
            Instance to be saved (or not).

        Returns
        -------
        ApplyResult
            Named tuple containing the result of the apply step.
        """
        model_name = model.__name__
        instance_id = local_instance.id

        remote_list = model.list(id__in=instance_id)
        if remote_list:
            remote_instance = remote_list[0]
            exclude_regex = self._model_to_regex.get(model_name, None)
            diff = DeepDiff(
                to_dict(local_instance),
                to_dict(remote_instance),
                exclude_regex_paths=exclude_regex,
            )
            if diff:
                bprint(
                    f"\nThe remote {model_name} with id {instance_id} has the "
                    " following differences with the local item:"
                )
                print(diff)
                update = typer.confirm(
                    "Do you want to update the local instance?"
                )
                if update:
                    return ApplyResult(True, to_dict(remote_instance))
                bprint(
                    f"\nYou are about to override the remote {model_name} "
                    f"with your local {model_name}:"
                )
                print(local_instance)
                update = typer.confirm("Are you sure?")
                if update:
                    local_instance.save()
                    return ApplyResult(True, to_dict(local_instance))
                return ApplyResult(False, to_dict(local_instance))
            bprint(
                f"Nothing to update, the same {model_name} was found "
                "remotely"
            )
            return ApplyResult(False, to_dict(local_instance))
        bprint(f"\nThe following {model_name} was not found remotely")
        print(local_instance)
        self._remove_ids(model_name, local_instance)
        bprint(f"\nYou are about to create the following {model_name}:")
        print(local_instance)
        create = typer.confirm("Are you sure?")
        if create:
            local_instance.save()
            remote_instance = model.retrieve(resource_id=local_instance.id)
            return ApplyResult(True, to_dict(remote_instance))
        return ApplyResult(False, to_dict(local_instance))

    def _remove_ids(self, model: SplightTypes, local_instance: SplightTypes):
        """Removes ids to a given dictionary representing a particular model.

        Parameters
        ----------
        model : SplightTypes
            Either an Asset, a Component or a RoutineObject.
        local_instance : SplightTypes
            Either an Asset, a Component or a RoutineObject.
        """

        if model == Asset.__name__:
            local_instance.id = None
            for attr in local_instance.attributes:
                attr.id = None
        else:
            local_instance.id = None
