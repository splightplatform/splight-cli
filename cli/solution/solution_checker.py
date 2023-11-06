from collections import namedtuple
from typing import List

from rich.console import Console
from splight_lib.models import Asset, Attribute, RoutineObject

from cli.solution.models import Component

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

    def check(self) -> CheckResult:
        """Looks for changes in the plan and adds them to the state file.

        Returns
        -------
        CheckResult
            The result after checking the assets and components.
        """
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

    def _check_assets(
        self, plan_assets: List[Asset], state_assets: List[Asset]
    ) -> List[Asset]:
        """Checks plan assets against state assets.

        Parameters
        ----------
        plan_assets : List[Asset]
            List of plan assets.
        state_assets : List[Asset]
            List of state assets.

        Returns
        -------
        List[Asset]
            List of state assets to delete.

        Raises
        ------
        ElemnentAlreadyDefined
            Raised when a plan asset is already defined.
        """
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
                        asset, state_assets[i]
                    )
                    break

        assets_to_delete = []
        unseen_state_assets = [
            k for k, v in seen_state_assets.items() if v == 0
        ]
        for idx in range(len(state_assets) - 1, -1, -1):
            state_asset_name = state_assets[idx].name
            if state_asset_name in unseen_state_assets:
                assets_to_delete.append(state_assets.pop(idx))

        return assets_to_delete

    def _update_asset(self, plan_asset: Asset, state_asset: Asset) -> Asset:
        """Updates a state asset based on the analogous plan asset.

        Parameters
        ----------
        plan_asset : Asset
            Plan asset.
        state_asset : Asset
            State Asset to update.

        Returns
        -------
        Asset
            The updated state asset.

        Raises
        ------
        ElemnentAlreadyDefined
            Raised when an attribute was defined twice.
        """
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
                        attr, state_asset.attributes[i]
                    )
                    break
        unseen_state_attributes = [
            k for k, v in seen_state_attributes.items() if v == 0
        ]
        for i in range(len(state_asset.attributes) - 1, -1, -1):
            if state_asset.attributes[i].name in unseen_state_attributes:
                state_asset.attributes.pop(i)

        return state_asset

    def _update_attribute(
        self, plan_attribute: Attribute, state_attribute: Attribute
    ) -> Attribute:
        """Updates the given state attribute.

        Parameters
        ----------
        plan_attribute : Attribute
            The plan attribute from which we will update the state attribute.
        state_attribute : Attribute
            The state attribute to update.

        Returns
        -------
        Attribute
            Returns the updated state attribute.
        """
        plan_attribute_dict = plan_attribute.dict(
            exclude_none=True,
            exclude_unset=True,
        )
        return state_attribute.copy(update=plan_attribute_dict)

    def _check_components(
        self,
        plan_components: List[Component],
        state_components: List[Component],
    ) -> List[Component]:
        """Checks plan components against state components.

        Parameters
        ----------
        plan_component : List[Component]
            List of plan components.
        state_component : List[Component]
            List of state components.

        Returns
        -------
        List[Component]
            List of state components to delete.

        Raises
        ------
        ElemnentAlreadyDefined
            Raised when a plan component is already defined.
        """
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
                        component, state_components[i]
                    )
                    break

        components_to_delete = []
        unseen_state_components = [
            k for k, v in seen_state_components.items() if v == 0
        ]
        for idx in range(len(state_components) - 1, -1, -1):
            state_component_name = state_components[idx].name
            if state_component_name in unseen_state_components:
                components_to_delete.append(state_components.pop(idx))

        return components_to_delete

    def _update_component(
        self, plan_component: Component, state_component: Component
    ) -> Component:
        """Updates a state component based on the analogous plan component.

        Parameters
        ----------
        plan_component : Component
            Plan component.
        state_component : Component
            State Component to update.

        Returns
        -------
        Component
            The updated state Component.

        Raises
        ------
        ElemnentAlreadyDefined
            Raised when a routine was defined twice.
        """
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
                        routine, state_component.routines[i]
                    )
                    break
        unseen_state_routines = [
            k for k, v in seen_state_routines.items() if v == 0
        ]
        for i in range(len(state_component.routines) - 1, -1, -1):
            if state_component.routines[i].name in unseen_state_routines:
                state_component.routines.pop(i)

        return state_component

    def _update_routine(
        self, plan_routine: RoutineObject, state_routine: RoutineObject
    ) -> RoutineObject:
        """Updates a state routine based on the plan routine.

        Parameters
        ----------
        plan_routine : RoutineObject
            A plan routine.
        state_routine : RoutineObject
            A state routine.

        Returns
        -------
        RoutineObject
            The state routine updated.
        """
        plan_routine_dict = plan_routine.dict(
            exclude_none=True,
            exclude_unset=True,
        )
        state_routine_dict = state_routine.dict()
        state_routine_dict.update(plan_routine_dict)

        return state_routine.parse_obj(state_routine_dict)
