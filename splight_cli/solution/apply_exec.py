from collections import namedtuple
from typing import Any, Dict

from deepdiff import DeepDiff
from rich import print as rprint
from splight_lib.models.component import Asset

from splight_cli.solution.exceptions import UndefinedID
from splight_cli.solution.models import StateSolution
from splight_cli.solution.utils import (
    SplightTypes,
    bprint,
    confirm_or_yes,
    to_dict,
)

ApplyResult = namedtuple("ApplyResult", ("update", "updated_dict"))


class ApplyExecutor:
    def __init__(
        self,
        state: StateSolution,
        yes_to_all: bool,
        regex_to_exclude: Dict[str, Any],
    ):
        self._state = state
        self._yes_to_all = yes_to_all
        self._model_to_regex = regex_to_exclude

    def apply(
        self,
        model: SplightTypes,
        local_instance: SplightTypes,
        not_found_is_exception: bool = False,
    ) -> ApplyResult:
        """Applies changes to the remote engine if needed.

        Parameters
        ----------
        model : SplightTypes
            A Splight model.
        local_instance : SplightTypes
            Instance to be saved (or not).
        not_found_is_exception : bool
            Raises an exception if the local instance (with an id) is not found
            remotely.

        Returns
        -------
        ApplyResult
            Named tuple containing the result of the apply step.
        """
        model_name = model.__name__
        instance_id = local_instance.id

        if instance_id is not None:
            return self._compare_with_remote(
                model, local_instance, not_found_is_exception
            )
        bprint(f"You are about to create the following {model_name}:")
        rprint(local_instance)
        create = confirm_or_yes(self._yes_to_all, "Are you sure?")
        if create:
            local_instance.save()
            remote_instance = model.retrieve(resource_id=local_instance.id)
            return ApplyResult(True, to_dict(remote_instance))
        return ApplyResult(False, to_dict(local_instance))

    def delete(self, model: SplightTypes, local_instance: SplightTypes):
        model_name = model.__name__

        bprint(f"You are about to delete the following {model_name}:")
        rprint(local_instance)
        should_delete = confirm_or_yes(self._yes_to_all, "Are you sure?")
        if should_delete:
            local_instance.delete()
            return ApplyResult(True, None)
        return ApplyResult(False, None)

    def _compare_with_remote(
        self,
        model: SplightTypes,
        local_instance: SplightTypes,
        not_found_is_exception: bool = False,
    ) -> ApplyResult:
        """Compares the local instance with the remote instances if any.

        Parameters
        ----------
        model : SplightTypes
            A Splight model.
        local_dict : SplightTypes
            Instance to be saved (or not).
        not_found_is_exception : bool
            Raises an exception if the local instance (with an id) is not found
            remotely.

        Returns
        -------
        ApplyResult
            Named tuple containing the result of the apply step.
        """
        model_name = model.__name__
        instance_id = local_instance.id

        remote_list = model.list(id__in=instance_id)
        if remote_list:
            remote_instance = remote_list[0]
            exclude_regex = self._model_to_regex.get(model_name, None)
            diff = DeepDiff(
                to_dict(local_instance),
                to_dict(remote_instance),
                exclude_regex_paths=exclude_regex,
            )
            if diff:
                bprint(
                    f"\nThe remote {model_name} with id {instance_id} has the "
                    " following differences with the local item:"
                )
                rprint(diff)
                update = confirm_or_yes(
                    self._yes_to_all,
                    "Do you want to update the local instance?",
                )
                if update:
                    return ApplyResult(True, to_dict(remote_instance))
                bprint(
                    f"\nYou are about to override the remote {model_name} "
                    f"with your local {model_name}:"
                )
                rprint(local_instance)
                update = confirm_or_yes(self._yes_to_all, "Are you sure?")
                if update:
                    local_instance.save()
                    remote_instance = model.retrieve(
                        resource_id=local_instance.id
                    )
                    return ApplyResult(True, to_dict(remote_instance))
                return ApplyResult(False, to_dict(local_instance))
            bprint(
                f"Nothing to update, the same {model_name} was found "
                "remotely"
            )
            return ApplyResult(False, to_dict(local_instance))
        if not_found_is_exception:
            raise UndefinedID(
                f"The {model_name} with id {instance_id} "
                f"(named: {local_instance.name}) was not found "
                "remotely, a valid remote id must be specified."
            )
        bprint(f"\nThe following {model_name} was not found remotely")
        rprint(local_instance)
        self._remove_ids(model_name, local_instance)
        bprint(f"\nYou are about to create the following {model_name}:")
        rprint(local_instance)
        create = confirm_or_yes(self._yes_to_all, "Are you sure?")
        if create:
            local_instance.save()
            remote_instance = model.retrieve(resource_id=local_instance.id)
            return ApplyResult(True, to_dict(remote_instance))
        return ApplyResult(False, to_dict(local_instance))

    def _remove_ids(self, model: SplightTypes, local_instance: SplightTypes):
        """Removes ids to a given dictionary representing a particular model.

        Parameters
        ----------
        model : SplightTypes
            Either an Asset, a Component or a RoutineObject.
        local_instance : SplightTypes
            Either an Asset, a Component or a RoutineObject.
        """

        if model == Asset.__name__:
            local_instance.id = None
            for attr in local_instance.attributes:
                attr.id = None
        else:
            local_instance.id = None
