from cli.solution.utils import StrKeyDict, bprint


class PlanExecutor:
    def __init__(self, state: StrKeyDict):
        self._state = state

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
