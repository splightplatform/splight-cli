from deepdiff import DeepDiff

from cli.solution.utils import bold_print


class ComparisonManager:
    @staticmethod
    def compare_dict(plan_dict, state_dict, exclude_regex=None):
        diff = DeepDiff(
            plan_dict, state_dict, exclude_regex_paths=exclude_regex
        )
        _name = plan_dict["name"]
        if diff:
            bold_print(
                f"{_name} have the following differences between plan and "
                "state file"
            )
            bold_print(diff)
        else:
            bold_print(
                f"{_name} have no differences between plan and state file"
            )

    @staticmethod
    def find_state_asset(asset_plan, state):
        if state is None:
            bold_print(
                "The following asset was not found in the state file. "
                "It will be created in the engine."
            )
            bold_print(asset_plan)
            return None
        state_assets = state["solution"]["assets"]
        for asset_state in state_assets:
            if asset_plan["name"] == asset_state["name"]:
                if asset_state["id"] is None:
                    bold_print(
                        "The following asset was found in the state file "
                        "with no id. It will be created in the engine."
                    )
                    bold_print(asset_plan)
                    return None
                return asset_state
