from typing import Callable, Dict, List, Optional, Union

from splight_lib.models.component import (
    InputDataAddress,
    InputParameter,
    Output,
    RoutineObject,
)

from splight_cli.solution.exceptions import UndefinedID
from splight_cli.solution.models import StateSolution
from splight_cli.solution.utils import get_ref_str, is_valid_uuid


class Replacer:
    _REF_TYPES = ["File", "Asset", "Attribute"]

    def __init__(self, state: StateSolution):
        self._state = state
        self._reference_map = {}
        self._attr_to_asset_map = {}

    def build_reference_map(self):
        """Builds a map that contains every possible reference."""
        for asset in self._state.assets + self._state.imported_assets:
            asset_ref = get_ref_str("asset", asset.name)
            self._reference_map[asset_ref] = asset.id
            for attr in asset.attributes:
                attr_ref = get_ref_str("attribute", attr.name)
                attr_ref = f"{asset_ref}.{attr_ref}"
                self._reference_map[attr_ref] = attr.id
                self._attr_to_asset_map[attr_ref] = asset_ref

        for file in self._state.files:
            file_ref = get_ref_str("file", file.name)
            self._reference_map[file_ref] = file.id

    def replace_references(self):
        """Replaces any references in the inputs, outputs and routines of every
        component.
        """
        state_components = self._state.components
        for i in range(len(state_components)):
            routines = state_components[i].routines
            component_name = state_components[i].name
            inputs = state_components[i].input
            for input_param in inputs:
                self._replace_io_ref(input_param, component_name)

            outputs = state_components[i].output
            for output_param in outputs:
                self._replace_io_ref(output_param, component_name)

            for routine in routines:
                self._replace_routine_ref(routine, component_name)

    def _replace_io_ref(
        self,
        io_elem: Union[InputDataAddress, InputParameter, Output],
        component_name: str,
        routine_name: Optional[str] = None,
    ):
        """Replaces references in any component input or output, the same
        is applied to elements in the routine config.

        Parameters
        ----------
        io_elem : Union[InputDataAddress, InputParameter, Output]
            Input or output element to replace with the corresponding
            reference.
        component_name : str
            The component name.
        routine_name : Optional[str]
            The routine name. Default None.
        """
        if io_elem.value is not None and io_elem.type in self._REF_TYPES:
            io_elem.value = self._get_new_value(
                io_elem, component_name, self._parse_input_output, routine_name
            )

    def _replace_routine_ref(
        self, routine: RoutineObject, component_name: str
    ):
        """Replaces assets and attributes to data addresses of a routine.

        Parameters
        ----------
        routine : RoutineObject
            The routine where we will replace the data addresses.
        component_name : str
            The component name.
        """
        for config in routine.config:
            self._replace_io_ref(config, component_name, routine.name)

        for io_elem in routine.input + routine.output:
            if io_elem.value is not None:
                io_elem.value = self._get_new_value(
                    io_elem,
                    component_name,
                    self._parse_data_addr,
                    routine.name,
                )

    def _get_new_value(
        self,
        elem: Union[InputDataAddress, InputParameter, Output],
        component_name: str,
        parse_fn: Callable,
        routine_name: Optional[str] = None,
    ) -> Union[List[Dict], Dict, List[str], str]:
        """Returns the id for some element if available

        Parameters
        ----------
        elem : Union[InputDataAddress, InputParameter, Output]
            Input or output element to replace with the corresponding
            reference.
        component_name : str
            The component name.
        parse_fn : callable
            The parse function to use.
        routine_name : Optional[str]
            The routine name. Default None.

        Returns
        -------
        Union[List[Dict], Dict, List[str], str]
            Input or output element where we have replaced the references with
            the ids.

        Raises
        ------
        ValueError
            Raised if passed a multiple: false element and a list value.
        """
        multiple = elem.multiple
        if not multiple and isinstance(elem.value, list):
            raise ValueError(
                f"Passed 'multiple: False' but value of {elem.name} is "
                "a list. Aborted."
            )
        if multiple:
            return [
                parse_fn(da, component_name, routine_name) for da in elem.value
            ]
        else:
            return parse_fn(elem.value, component_name, routine_name)

    def _parse_input_output(
        self, value_ref: str, component_name: str, routine_name: str
    ) -> str:
        """Parse function for component inputs or outputs.

        Parameters
        ----------
        value_ref : str
            Reference to replace.
        component_name : str
            The name of the component in question.
        routine_name : str
            The name of the routine in question.

        Returns
        -------
        str
            ID string if available.

        Raises
        ------
        UndefinedID
            Raised if the value reference passed is not a valid reference.
        """
        is_uuid = is_valid_uuid(value_ref)
        if is_uuid:
            self._check_id_is_defined(value_ref)
            return value_ref
        if value_ref not in self._reference_map:
            raise UndefinedID(
                f"The reference '{value_ref}' used in the component named "
                f"'{component_name}' is not a valid reference."
            )
        return self._reference_map[value_ref]

    def _parse_data_addr(
        self, data_addr: Dict[str, str], component_name: str, routine_name: str
    ) -> Dict[str, str]:
        """Parse function for data addresses.

        Parameters
        ----------
        data_addr : Dict[str, str]
            Data Address where we want to update the ids.
        component_name : str
            The name of the component in question.
        routine_name : str
            The name of the routine in question.

        Returns
        -------
        Dict[str, str]
            A dictionary containing the data address ids (if available).

        Raises
        ------
        UndefinedID
            Raised if the value reference passed is not a valid reference.
        """
        asset_ref = data_addr.asset
        attr_ref = data_addr.attribute

        asset_is_id = is_valid_uuid(asset_ref)
        attr_is_id = is_valid_uuid(attr_ref)
        if asset_is_id or attr_is_id:
            self._check_id_is_defined(asset_ref)
            self._check_id_is_defined(attr_ref)
            return {"asset": asset_ref, "attribute": attr_ref}

        missing_ref = None
        if asset_ref not in self._reference_map:
            missing_ref = asset_ref
        elif attr_ref not in self._reference_map:
            missing_ref = attr_ref

        if self._attr_to_asset_map[attr_ref] != asset_ref:
            raise UndefinedID(
                f"The attribute '{attr_ref}' is not an attribute of "
                f"the asset '{asset_ref}' which is defined in the "
                f"'{routine_name}' of the component '{component_name}'."
            )

        if missing_ref is not None:
            raise UndefinedID(
                f"The reference '{missing_ref}' "
                f"used in the routine named '{routine_name}' of the "
                f"component '{component_name}' is not a valid reference."
            )
        return {
            "asset": self._reference_map[asset_ref],
            "attribute": self._reference_map[attr_ref],
        }

    def _check_id_is_defined(self, value_ref: str, component_name: str):
        if value_ref not in self._reference_map.values():
            raise UndefinedID(
                f"The id: {value_ref} used in the component named "
                f"{component_name} is not defined."
            )
