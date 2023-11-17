from typing import Any, Dict, Type

from deepdiff import DeepDiff

from splight_cli.solution.models import StateSolution
from splight_cli.solution.solution_checker import CheckResult
from splight_cli.solution.utils import SplightTypes, bprint, to_dict


class MissingDataAddress(Exception):
    ...


class PlanExecutor:
    def __init__(self, state: StateSolution, regex_to_exclude: Dict[str, Any]):
        self._state = state
        self._model_to_regex = regex_to_exclude

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

    def plan_elem_state(
        self, elem_type: Type[SplightTypes], state_elem: SplightTypes
    ):
        """Shows what is going to happen to a certain Asset, Component,
        RoutineObject or File if the plan is applied.

        Parameters
        ----------
        state_elem : SplightTypes
            The state asset, component, routine or file to analyze.
        """
        instance_id = state_elem.id

        if instance_id is not None:
            return self._compare_with_remote(elem_type, state_elem)
        bprint(f"The following {elem_type.__name__} will be created:")
        bprint(state_elem)

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
