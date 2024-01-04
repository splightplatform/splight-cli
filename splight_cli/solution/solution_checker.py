from collections import namedtuple
from typing import Callable, List, Type

from rich.console import Console
from splight_lib.models import (
    Alert,
    AlertItem,
    Asset,
    Attribute,
    File,
    Function,
    FunctionItem,
    RoutineObject,
    Secret,
)
from splight_lib.models.alert import AlertThreshold
from splight_lib.models.asset import GeometryCollection

from splight_cli.solution.exceptions import ElemnentAlreadyDefined
from splight_cli.solution.models import Component
from splight_cli.solution.utils import SplightTypes

CheckResult = namedtuple(
    "CheckResult",
    (
        "assets_to_delete",
        "secrets_to_delete",
        "files_to_delete",
        "components_to_delete",
        "functions_to_delete",
        "alerts_to_delete",
        "plan",
        "state",
    ),
)

console = Console()


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
        assets_to_delete = self._check_elements(
            self._plan.assets,
            self._state.assets,
            Asset.__name__,
            self._update_asset,
        )
        assets_to_delete += self._check_elements(
            self._plan.imported_assets,
            self._state.imported_assets,
            Asset.__name__,
            self._update_asset,
        )
        secrets_to_delete = self._check_elements(
            self._plan.secrets,
            self._state.secrets,
            Secret.__name__,
            self._update_secret,
        )
        secrets_to_delete += self._check_elements(
            self._plan.imported_secrets,
            self._state.imported_secrets,
            Secret.__name__,
            self._update_secret,
        )
        files_to_delete = self._check_elements(
            self._plan.files,
            self._state.files,
            File.__name__,
            self._update_file,
        )
        functions_to_delete = self._check_elements(
            self._plan.functions,
            self._state.functions,
            Function.__name__,
            self._update_function,
        )
        functions_to_delete += self._check_elements(
            self._plan.imported_functions,
            self._state.imported_functions,
            Function.__name__,
            self._update_function,
        )
        alerts_to_delete = self._check_elements(
            self._plan.alerts,
            self._state.alerts,
            Alert.__name__,
            self._update_alert,
        )
        alerts_to_delete += self._check_elements(
            self._plan.imported_alerts,
            self._state.imported_alerts,
            Alert.__name__,
            self._update_alert,
        )
        components_to_delete = self._check_elements(
            self._plan.components,
            self._state.components,
            Component.__name__,
            self._update_component,
        )
        components_to_delete += self._check_elements(
            self._plan.imported_components,
            self._state.imported_components,
            Component.__name__,
            self._update_component,
        )

        return CheckResult(
            assets_to_delete=assets_to_delete,
            secrets_to_delete=secrets_to_delete,
            files_to_delete=files_to_delete,
            components_to_delete=components_to_delete,
            functions_to_delete=functions_to_delete,
            alerts_to_delete=alerts_to_delete,
            plan=self._plan,
            state=self._state,
        )

    def _check_elements(
        self,
        plan_elements: List[SplightTypes],
        state_elements: List[SplightTypes],
        elem_type: Type[SplightTypes],
        update_fn: Callable,
        accesor: str = "name",
    ) -> List[SplightTypes]:
        """Checks if the element is already defined and/or if it was removed.

        Parameters
        ----------
        plan_elements : List[SplightTypes]
            Plan elements to analyze.
        state_elements : List[SplightTypes]
            State elements to analyze.
        elem_type : Type[SplightTypes]
            Type of the elements to analyze.
        update_fn : Callable
            Function to be used to update an element.

        Returns
        -------
        List[SplightTypes]
            A list of elements to be deleted, if any.

        Raises
        ------
        ElemnentAlreadyDefined
            Raised when the element was already defined.
        """
        seen_state_elems = {getattr(e, accesor): 0 for e in state_elements}
        for idx, elem in enumerate(plan_elements):
            plan_elem_name = getattr(elem, accesor)
            if plan_elem_name not in seen_state_elems.keys():
                state_elements.insert(idx, elem)
                seen_state_elems[plan_elem_name] = 1
                continue
            seen_state_elems[plan_elem_name] += 1
            if seen_state_elems[plan_elem_name] > 2:
                raise ElemnentAlreadyDefined(
                    f"The {elem_type} {plan_elem_name} is already defined."
                    f"{elem_type} names must be unique."
                )
            for i in range(len(state_elements)):
                if getattr(state_elements[i], accesor) == plan_elem_name:
                    state_elements[i] = update_fn(elem, state_elements[i])
                    break

        elems_to_delete = []
        unseen_state_elements = {
            k for k, v in seen_state_elems.items() if v == 0
        }
        for idx in range(len(state_elements) - 1, -1, -1):
            state_elem_name = getattr(state_elements[idx], accesor)
            if state_elem_name in unseen_state_elements:
                elems_to_delete.append(state_elements.pop(idx))

        return elems_to_delete

    def _update_asset(self, plan_asset: Asset, state_asset: Asset) -> Asset:
        """Function to update an Asset.

        Parameters
        ----------
        plan_asset : Asset
            Plan asset.
        state_asset : Asset
            State asset to be updated based on the plan asset.

        Returns
        -------
        Asset
            Updated asset.
        """
        plan_asset_dict = plan_asset.model_dump(
            exclude={"attributes", "geomtry"},
            exclude_none=True,
            exclude_unset=True,
        )
        state_asset = state_asset.model_copy(update=plan_asset_dict)
        self._check_elements(
            plan_asset.attributes,
            state_asset.attributes,
            Attribute.__name__,
            self._update_attribute,
        )
        if geometry := plan_asset_dict.get("geometry", {}):
            state_asset.geometry = GeometryCollection.model_validate(geometry)
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
            The state attribute to updated.

        Returns
        -------
        Attribute
            Returns the updated state attribute.
        """
        plan_attribute_dict = plan_attribute.model_dump(
            exclude_none=True,
            exclude_unset=True,
        )
        return state_attribute.model_copy(update=plan_attribute_dict)

    def _update_secret(
        self, plan_secret: Secret, state_secret: Secret
    ) -> Secret:
        """Updates the given state secret.

        Parameters
        ----------
        plan_secret : Secret
            Plan secret.
        state_secret : Secret
            State secret to be updated based on the plan secret.

        Returns
        -------
        secret
            Updated secret.
        """
        plan_secret_dict = plan_secret.model_dump(
            exclude_none=True,
            exclude_unset=True,
        )
        plan_secret_dict.pop("secret", None)
        return state_secret.model_copy(update=plan_secret_dict)

    def _update_file(self, plan_file: File, state_file: File) -> File:
        """Updates the given state file.

        Parameters
        ----------
        plan_file : File
            Plan file.
        state_file : File
            State file to be updated based on the plan file.

        Returns
        -------
        File
            Updated file.
        """
        plan_file_dict = plan_file.model_dump(
            exclude_none=True,
            exclude_unset=True,
        )
        plan_file_dict.pop("file", None)
        return state_file.model_copy(update=plan_file_dict)

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
        """
        plan_component_dict = plan_component.model_dump(
            exclude={"routines"},
            exclude_none=True,
            exclude_unset=True,
        )
        state_component_dict = state_component.model_dump()
        state_component_dict.update(plan_component_dict)
        state_component = state_component.model_validate(state_component_dict)

        self._check_elements(
            plan_component.routines,
            state_component.routines,
            RoutineObject.__name__,
            self._update_routine,
        )

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
            A state routine to update.

        Returns
        -------
        RoutineObject
            The updated state routine.
        """
        plan_routine_dict = plan_routine.model_dump(
            exclude_none=True,
            exclude_unset=True,
        )
        state_routine_dict = state_routine.model_dump()
        state_routine_dict.update(plan_routine_dict)

        return state_routine.model_validate(state_routine_dict)

    def _update_function(
        self, plan_function: Function, state_function: Function
    ):
        plan_function_dict = plan_function.model_dump(
            exclude_none=True, exclude_unset=True, exclude={"function_items"}
        )
        state_function = state_function.model_copy(update=plan_function_dict)
        self._check_elements(
            plan_function.function_items,
            state_function.function_items,
            FunctionItem.__name__,
            self._update_function_item,
            accesor="ref_id",
        )
        return state_function

    def _update_function_item(
        self,
        plan_function_item: FunctionItem,
        state_function_item: FunctionItem,
    ):
        plan_function_item_dict = plan_function_item.model_dump(
            exclude_none=True,
            exclude_unset=True,
        )
        return state_function_item.model_copy(update=plan_function_item_dict)

    def _update_alert(self, plan_alert: Alert, state_alert: Alert):
        plan_alert_dict = plan_alert.model_dump(
            exclude_none=True, exclude_unset=True, exclude={"alert_items"}
        )
        state_alert = state_alert.model_copy(update=plan_alert_dict)

        state_alert.stmt_thresholds = []
        for threshold in plan_alert_dict["stmt_thresholds"]:
            state_alert.stmt_thresholds.append(
                AlertThreshold.model_validate(threshold)
            )

        self._check_elements(
            plan_alert.alert_items,
            state_alert.alert_items,
            AlertItem.__name__,
            self._update_alert_item,
            accesor="ref_id",
        )
        return state_alert

    def _update_alert_item(
        self,
        plan_alert_item: AlertItem,
        state_alert_item: AlertItem,
    ):
        plan_alert_item_dict = plan_alert_item.model_dump(
            exclude_none=True,
            exclude_unset=True,
        )
        return state_alert_item.model_copy(update=plan_alert_item_dict)
