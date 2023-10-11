from cli.solution.comparison import ComparisonManager
from cli.solution.utils import bold_print, load_yaml


class SolutionManager:
    _EXCLUDE_ID_REGEX = "\['id'\]"

    def __init__(self):
        self._comparison = ComparisonManager()

    def plan(self, yaml_file: str, state_file: str):
        plan = load_yaml(yaml_file)
        state = load_yaml(state_file) if state_file else None
        self._assets_plan(plan, state)
        # self._components_plan(...)

    def _assets_plan(self, plan, state):
        bold_print("\nComparing Assets...")
        assets_list = plan["solution"]["assets"]
        for asset_plan in assets_list:
            asset_state = self._comparison.find_state_asset(asset_plan, state)
            if asset_state is not None:
                self._comparison.compare_dict(
                    asset_plan, asset_state, self._EXCLUDE_ID_REGEX
                )
