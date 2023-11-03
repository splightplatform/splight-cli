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

        components_to_delete = self._check_components(
            self._plan.components, self._state.components
        )
        components_to_delete += self._check_components(
            self._plan.imported_components, self._state.imported_components
        )

        return CheckResult(
            assets_to_delete=assets_to_delete,
            components_to_delete=components_to_delete,
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

    def _update_asset(self, plan_asset, state_asset):
        plan_asset_dict = plan_asset.dict(
            exclude={"attributes"}, exclude_none=True, exclude_unset=True
        )
        state_asset = state_asset.copy(update=plan_asset_dict)

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
                    f"Attribute names must be unique."
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

    def _update_attribute(self, plan_attribute, state_attribute):
        plan_attribute_dict = plan_attribute.dict(
            exclude_none=True,
            exclude_unset=True,
        )
        return state_attribute.copy(update=plan_attribute_dict)

    def _check_components(self, plan_components, state_components):
        seen_state_components = {a.name: 0 for a in state_components}
        for idx, component in enumerate(plan_components):
            plan_component_name = component.name
            if plan_component_name not in seen_state_components.keys():
                state_components.insert(idx, component)
                seen_state_components[plan_component_name] = 1
                continue
            seen_state_components[plan_component_name] += 1
            if seen_state_components[plan_component_name] > 2:
                raise ElemnentAlreadyDefined(
                    f"The component {plan_component_name} is already defined."
                    f"Component names must be unique."
                )
            for i in range(len(state_components)):
                if state_components[i].name == plan_component_name:
                    state_components[i] = self._update_component(
                        state_components[i], component
                    )
                    break

        components_to_delete = []
        unseen_state_components = [
            k for k, v in seen_state_components.items() if v == 0
        ]
        for idx in range(len(state_components) - 1, 0, -1):
            state_component_name = state_components[idx].name
            if state_component_name in unseen_state_components:
                components_to_delete.append(state_components.pop(idx))

        return components_to_delete

    def _update_component(self, plan_component, state_component):
        plan_component_dict = plan_component.dict(
            exclude={"routines"},
            exclude_none=True,
            exclude_unset=True,
        )
        state_component = state_component.copy(update=plan_component_dict)

        seen_state_routines = {r.name: 0 for r in state_component.routines}
        for idx, routine in enumerate(plan_component.routines):
            plan_routine_name = routine.name
            if plan_routine_name not in seen_state_routines:
                state_component.routines.insert(idx, routine)
                seen_state_routines[plan_routine_name] = 1
            seen_state_routines[plan_routine_name] += 1
            if seen_state_routines[plan_routine_name] > 2:
                raise ElemnentAlreadyDefined(
                    f"The attribute {plan_routine_name} is already defined."
                    f"Attribute names must be unique."
                )
            for i in range(len(state_component.routines)):
                if state_component.routines[i].name == plan_routine_name:
                    state_component.routines[i] = self._update_routine(
                        state_component.routines[i], routine
                    )
                    break
        unseen_state_routines = [
            k for k, v in seen_state_routines.items() if v == 0
        ]
        for i in range(len(state_component.routines) - 1, 0, -1):
            if state_component.routines[i].name in unseen_state_routines:
                state_component.routines.pop(i)

        return state_component

    def _update_routine(self, plan_routine, state_routine):
        plan_routine_dict = plan_routine.dict(
            exclude_none=True,
            exclude_unset=True,
        )
        state_routine_dict = state_routine.dict()
        state_routine_dict.update(plan_routine_dict)

        return state_routine.parse_obj(state_routine_dict)
