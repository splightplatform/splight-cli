from collections import namedtuple

from rich.console import Console

CheckResult = namedtuple(
    "CheckResult",
    ("assets_to_delete", "components_to_delete", "plan", "state"),
)

console = Console()


class ElemnentAlreadyDefined(Exception):
    ...


class SolutionChecker:
    def __init__(self, plan, state):
        self._plan = plan
        self._state = state

    def check(self):
        assets_to_delete = self._check_assets()
        # self._replace_plan_components()

        return CheckResult(
            assets_to_delete=assets_to_delete,
            components_to_delete=[],
            plan=self._plan,
            state=self._state,
        )

    def _check_assets(self):
        plan_assets, state_assets = self._plan.assets, self._state.assets
        seen_state_assets = {a.name: 0 for a in state_assets}
        for idx, asset in enumerate(plan_assets):
            plan_asset_name = asset.name
            seen_state_assets[plan_asset_name] += 1
            if plan_asset_name not in seen_state_assets.keys():
                state_assets.insert(idx, asset)
                seen_state_assets[plan_asset_name] = 1
                continue
            if seen_state_assets[plan_asset_name] > 2:
                raise ElemnentAlreadyDefined(
                    f"The asset {plan_asset_name} is already defined."
                    f"Asset names must be unique."
                )

        imported_plan_assets = self._plan.imported_assets
        imported_state_assets = self._state.imported_assets
        seen_state_assets = {a.name: 0 for a in imported_state_assets}
        for idx, asset in enumerate(imported_plan_assets):
            plan_asset_name = asset.name
            if plan_asset_name not in seen_state_assets.keys():
                imported_state_assets.insert(idx, asset)
                seen_state_assets[plan_asset_name] = 1
                continue
            seen_state_assets[plan_asset_name] += 1
            if seen_state_assets[plan_asset_name] > 2:
                raise ElemnentAlreadyDefined(
                    f"The asset {plan_asset_name} is already defined."
                    f"Asset names must be unique."
                )

        assets_to_delete = []
        seen_plan_assets = [a.name for a in plan_assets]
        for idx in range(len(state_assets)):
            state_asset_name = state_assets[idx].name
            if state_asset_name not in seen_plan_assets:
                assets_to_delete.append(state_assets.pop(idx))

        seen_plan_assets = [a.name for a in imported_plan_assets]
        for idx in range(len(imported_state_assets)):
            state_asset_name = imported_state_assets[idx].name
            if state_asset_name not in seen_plan_assets:
                assets_to_delete.append(imported_state_assets.pop(idx))

        return assets_to_delete
