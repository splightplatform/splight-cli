from deepdiff import DeepDiff

from cli.solution.utils import StrKeyDict, bprint, parse_str_data_addr


class MissingDataAddress(Exception):
    ...


class PlanExecutor:
    def __init__(self, state: StrKeyDict):
        self._state = state

        self._possible_asset_attr = set()
        for asset in self._state["solution"]["assets"]:
            asset_name = asset["name"]
            for attr in asset["attributes"]:
                attr_name = attr["name"]
                self._possible_asset_attr.add(f"{asset_name}-{attr_name}")

    def compare_state_asset(self, asset_plan: StrKeyDict):
        """Finds and compares an asset from the plan with the analogous in the
        state file printing the plan in case it's executed.

        Parameters
        ----------
        asset_plan : StrKeyDict
            An Asset instance as a dictionary.
        """
        state_assets = self._state["solution"]["assets"]
        for i in range(len(state_assets)):
            if asset_plan["name"] == state_assets[i]["name"]:
                if state_assets[i]["id"] is None:
                    bprint(
                        "The following asset was found in the state file "
                        "with no id. It will be created in the engine."
                    )
                    bprint(asset_plan)
                    break
                bprint(
                    "The following asset was found in the state file with id "
                    f"{state_assets[i]['id']}. It will be updated in the "
                    "engine."
                )
                bprint(state_assets[i])
                break

    def compare_state_component(self, plan_component: StrKeyDict):
        """Finds and compares an asset from the plan with the analogous in the
        state file printing the plan in case it's executed.

        Parameters
        ----------
        asset_plan : StrKeyDict
            An Asset instance as a dictionary.
        """
        state_components = self._state["solution"]["components"]
        state_component_found = None
        for i in range(len(state_components)):
            if plan_component["name"] == state_components[i]["name"]:
                state_component_found = state_components[i]
                break

        self._check_assets_are_defined(state_component_found)
        diff = DeepDiff(
            plan_component,
            state_component_found,
            exclude_regex_paths=[
                r"\['id'\]",
                r"\['input'\]\[\d+\]\['value'\]",
                r"\['output'\]\[\d+\]\['value'\]",
            ],
        )
        if diff:
            bprint(
                f"The component {plan_component['name']} was found in the "
                "state file with the following differences with respect to "
                "the plan file."
            )
            bprint(diff)
            return
        if state_component_found["id"] is None:
            bprint(
                f"The following component named {plan_component['name']} was "
                "found in the state file with no id. It will be created in "
                "the engine."
            )
            bprint(state_component_found)
            return

        bprint(
            "The following component was found in the state file "
            f"with id {state_component_found['id']}. It will be updated "
            "if any difference is found with respect to the engine."
        )
        bprint(state_component_found)

    def _check_assets_are_defined(self, state_component_found: StrKeyDict):
        """Checks if the assets of a component are defined or not in the state
        file.

        Parameters
        ----------
        state_component_found : StrKeyDict
            The state component.
        """
        routines = state_component_found.get("routines", [])
        for routine in routines:
            for io_elem in routine["input"] + routine["output"]:
                if io_elem.get("value", None) is not None:
                    self._is_state_asset_attr(io_elem)

    def _is_state_asset_attr(self, io_elem: StrKeyDict):
        """Raises an exception if an asset is not defined in the state file.

        Parameters
        ----------
        io_elem : StrKeyDict
            Input or output dictionary element.

        Raises
        ------
        MissingDataAddress
            Raised when an asset is not defined in the state file.
        """
        multiple = io_elem.get("multiple", False)
        io_values = io_elem["value"] if multiple else [io_elem["value"]]
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
