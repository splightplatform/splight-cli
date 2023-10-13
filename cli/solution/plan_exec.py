from deepdiff import DeepDiff

from cli.solution.utils import StrKeyDict, bprint


class MissingDataAddress(Exception):
    ...


class PlanExecutor:
    def __init__(self, state: StrKeyDict):
        self._state = state

        self._possible_asset_attr = set()
        for asset in self._state["solution"]["assets"]:
            asset_id = asset["id"]
            for attr in asset["attributes"]:
                attr_id = attr["id"]
                self._possible_asset_attr.add(f"{asset_id}-{attr_id}")

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
            exclude_regex_paths=["\['id'\]", "\['value'\]"],
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
        routines = state_component_found.get("routines", [])
        for routine in routines:
            for _input in routine["input"]:
                if _input.get("value", None) is not None:
                    self._is_possible_asset_attr(_input)
            for _output in routine["output"]:
                if _input.get("value", None) is not None:
                    self._is_possible_asset_attr(_output)

    def _is_possible_asset_attr(self, io_elem: StrKeyDict):
        multiple = io_elem.get("multiple", False)
        input_value = io_elem["value"] if multiple else [io_elem["value"]]
        for data_addr in input_value:
            ids_str = f"{data_addr['asset']}-{data_addr['attribute']}"
            if ids_str not in self._possible_asset_attr:
                raise MissingDataAddress(
                    f"The asset id: {data_addr['asset']} "
                    f"attribute id: {data_addr['attribute']} is "
                    "not defined in the state file. Aborted."
                )
