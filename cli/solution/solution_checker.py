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
        assets_to_delete = self._check_assets(
            self._plan.assets, self._state.assets
        )
        assets_to_delete += self._check_assets(
            self._plan.imported_assets, self._state.imported_assets
        )

        # self._replace_plan_components()

        return CheckResult(
            assets_to_delete=assets_to_delete,
            components_to_delete=[],
            plan=self._plan,
            state=self._state,
        )

    def _check_assets(self, plan_assets, state_assets):
        seen_state_assets = {a.name: 0 for a in state_assets}
        for idx, asset in enumerate(plan_assets):
            plan_asset_name = asset.name
            if plan_asset_name not in seen_state_assets.keys():
                state_assets.insert(idx, asset)
                seen_state_assets[plan_asset_name] = 1
                continue
            seen_state_assets[plan_asset_name] += 1
            if seen_state_assets[plan_asset_name] > 2:
                raise ElemnentAlreadyDefined(
                    f"The asset {plan_asset_name} is already defined."
                    f"Asset names must be unique."
                )
            for i in range(len(state_assets)):
                if state_assets[i].name == plan_asset_name:
                    state_assets[i] = self._update_asset(
                        state_assets[i], asset
                    )
                    break

        assets_to_delete = []
        unseen_state_assets = [
            k for k, v in seen_state_assets.items() if v == 0
        ]
        for idx in range(len(state_assets) - 1, 0, -1):
            state_asset_name = state_assets[idx].name
            if state_asset_name in unseen_state_assets:
                assets_to_delete.append(state_assets.pop(idx))

        return assets_to_delete

    def _update_asset(self, state_asset, plan_asset):
        plan_asset_dict = plan_asset.dict(
            exclude={"attributes"},
            exclude_none=True,
            exclude_unset=True,
            exclude_defaults=True,
        )
        state_asset = state_asset.copy(update=plan_asset_dict)

        plan_asset_dict = plan_asset.dict()
        seen_state_attributes = {a.name: 0 for a in state_asset.attributes}
        for idx, attr in enumerate(plan_asset.attributes):
            plan_attr_name = attr.name
            if plan_attr_name not in seen_state_attributes:
                state_asset.attributes.insert(idx, attr)
                seen_state_attributes[plan_attr_name] = 1
            seen_state_attributes[plan_attr_name] += 1
            if seen_state_attributes[plan_attr_name] > 2:
                raise ElemnentAlreadyDefined(
                    f"The attribute {plan_attr_name} is already defined."
                    f"Asset names must be unique."
                )
            for i in range(len(state_asset.attributes)):
                if state_asset.attributes[i].name == plan_attr_name:
                    state_asset.attributes[i] = self._update_attribute(
                        state_asset.attributes[i], attr
                    )
                    break
        unseen_state_attributes = [
            k for k, v in seen_state_attributes.items() if v == 0
        ]
        for i in range(len(state_asset.attributes) - 1, 0, -1):
            if state_asset.attributes[i].name in unseen_state_attributes:
                state_asset.attributes.pop(i)

        return state_asset

    def _update_attribute(self, state_attribute, plan_attribute):
        plan_attribute_dict = plan_attribute.dict(
            exclude_none=True, exclude_unset=True, exclude_defaults=True
        )
        return state_attribute.copy(update=plan_attribute_dict)
