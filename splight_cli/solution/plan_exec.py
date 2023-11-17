from typing import Any, Dict, Type

from deepdiff import DeepDiff
from splight_lib.models.component import Asset, Component, RoutineObject

from splight_cli.solution.models import StateSolution
from splight_cli.solution.solution_checker import CheckResult
from splight_cli.solution.utils import SplightTypes, bprint, to_dict


class PlanExecutor:
    def __init__(self, state: StateSolution, regex_to_exclude: Dict[str, Any]):
        self._state = state
        self._model_to_regex = regex_to_exclude
        self._possible_asset_attr = set()
        for asset in self._state.assets:
            asset_name = asset.name
            for attr in asset.attributes:
                attr_name = attr.name
                self._possible_asset_attr.add(f"{asset_name}-{attr_name}")

    def plan_elements_to_delete(self, check_results: CheckResult):
        """Shows which elements (assets or component) are going to be removed
        if the plan were to be applied.

        Parameters
        ----------
        check_results : CheckResult
            The result solution checker.
        """
        for asset in check_results.assets_to_delete:
            bprint(
                "If the plan is applied the following Asset will be deleted:"
            )
            bprint(asset)
        for component in check_results.components_to_delete:
            bprint(
                "If the plan is applied the following Component will be "
                "deleted:"
            )
            bprint(component)

    def plan_asset_state(self, state_asset: Asset):
        """Shows what is going to happen to a certain Asset if the plan is
        applied.

        Parameters
        ----------
        state_asset : Asset
            The state asset to analyze.
        """
        instance_id = state_asset.id

        if instance_id is not None:
            return self._compare_with_remote(Asset, state_asset)
        bprint(f"The following Asset will be created:")
        bprint(state_asset)

    def plan_component_state(self, state_component: Component):
        """Shows what is going to happen to a certain Component if the plan is
        applied.

        Parameters
        ----------
        state_component : Component
            The state component to analyze.
        """
        instance_id = state_component.id
        if instance_id is not None:
            return self._compare_with_remote(Component, state_component)
        bprint(f"The following Component will be created:")
        bprint(state_component)

    def plan_routine_state(self, state_routine: RoutineObject):
        """Shows what is going to happen to a certain Routine if the plan is
        applied.

        Parameters
        ----------
        state_routine : RoutineObject
            The state routine of a given component to analyze.
        """
        instance_id = state_routine.id
        if instance_id is not None:
            return self._compare_with_remote(RoutineObject, state_routine)
        bprint(f"The following Routine will be created:")
        bprint(state_routine)

    def _compare_with_remote(
        self, model: Type[SplightTypes], local_instance: SplightTypes
    ):
        """Compares the given local_instance to the remote analogous.

        Parameters
        ----------
        model : Type[SplightTypes]
            A Splight type.
        local_instance : SplightTypes
            The instance to analyze.
        """
        model_name = model.__name__
        instance_id = local_instance.id
        instance_name = local_instance.name

        remote_list = model.list(id__in=instance_id)
        if remote_list:
            remote_instance = remote_list[0]
            exclude_regex = self._model_to_regex.get(model_name, None)
            diff = DeepDiff(
                to_dict(remote_instance),
                to_dict(local_instance),
                exclude_regex_paths=exclude_regex,
            )
            if diff:
                bprint(
                    f"\nThe remote {model_name} named {instance_name} with id "
                    f" {instance_id} has the following differences with the "
                    "local item:"
                )
                bprint(diff)
                return
            bprint(
                f"Nothing to update, the same {model_name} named "
                f"{instance_name} was found remotely as defined locally."
            )
            return
        bprint(
            f"\nThe following {model_name} named {instance_name} was not "
            "found remotely. It will be created if the plan is applied."
        )
        bprint(local_instance)
