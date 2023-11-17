from typing import Dict, List, Union

from splight_lib.models.component import InputDataAddress, RoutineObject

from splight_cli.solution.exceptions import UndefinedID
from splight_cli.solution.models import StateSolution
from splight_cli.solution.utils import MatchResult, parse_str_data_addr


class Replacer:
    def __init__(self, state: StateSolution):
        self._state = state
        self._is_planning = True

    def replace_data_addr(self, is_planning: bool):
        """Replaces assets data addresses in routines's inputs and outputs.

        Parameters
        ----------
        is_pĺanning : bool
            Whether the operation is being executed in a planning command or
            in an apply command.
        """
        self._is_planning = is_planning
        state_components = self._state.components
        for i in range(len(state_components)):
            routines = state_components[i].routines
            component_name = state_components[i].name
            for routine in routines:
                self._replace_routine_data_addr(routine, component_name)

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
            self._check_ids_are_defined(result)
            return {"asset": result.asset, "attribute": result.attribute}
        state_assets = self._state.assets
        asset_id, attr_id = None, None
        for asset in filter(lambda x: x.name == result.asset, state_assets):
            asset_id = asset.id
            for attr in filter(
                lambda x: x.name == result.attribute, asset.attributes
            ):
                attr_id = attr.id
                if self._is_planning:
                    return {"asset": asset_id, "attribute": attr_id}
                break
            break
        if asset_id is None or attr_id is None:
            raise UndefinedID(
                f"The asset: '{result.asset}' attribute: '{result.attribute}' "
                f"used in the routine named '{routine_name}' of the "
                f"component '{component_name}' is not defined in the plan."
            )
        return {"asset": asset_id, "attribute": attr_id}

    def _check_ids_are_defined(self, result: MatchResult):
        """Checks if an asset id is defined in the state file.

        Parameters
        ----------
        result : MatchResult
            The result from parsing the asset string.

        Raises
        ------
        UndefinedID
            raised when the asset is not found in the state file.
        """
        every_asset = self._state.assets + self._state.imported_assets
        for asset in filter(lambda x: x.id == result.asset, every_asset):
            for attr in filter(
                lambda x: x.id == result.attribute, asset.attributes
            ):
                return
        raise UndefinedID(
            f"Routine Error: The asset: {result.asset} attribute: "
            f"{result.attribute} is not defined in the state file."
        )
