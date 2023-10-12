from collections import namedtuple

import typer
from deepdiff import DeepDiff
from rich import print
from splight_lib.models import Asset

from cli.solution.utils import SplightTypes, StrKeyDict, bprint, to_dict

ApplyResult = namedtuple("ApplyResult", ("update", "updated_dict"))


class ApplyExecutor:
    def __init__(self, state: StrKeyDict):
        self._state = state

    def execute(self, model: SplightTypes, local_dict: StrKeyDict):
        model_name = model.__name__
        instance_id = local_dict["id"]

        if instance_id is not None:
            return self._compare_with_remote(model, local_dict)
        bprint(f"You are about to create the following {model_name}:")
        print(local_dict)
        create = typer.confirm("Are you sure?")
        if create:
            local_instance = model.parse_obj(local_dict)
            local_instance.save()
            remote_instance = model.retrieve(resource_id=local_instance.id)
            return ApplyResult(True, to_dict(remote_instance))
        return ApplyResult(False, None)

    def _compare_with_remote(
        self, model: SplightTypes, local_dict: StrKeyDict
    ):
        model_name = model.__name__
        instance_id = local_dict["id"]

        remote_list = model.list(id__in=instance_id)
        if remote_list:
            remote_instance = remote_list[0].dict()
            diff = DeepDiff(local_dict, remote_instance)
            if diff:
                bprint(
                    f"\nThe remote {model_name} with id {instance_id} has the "
                    " following differences with the local item:"
                )
                print(diff)
                update = typer.confirm(
                    "Do you want to update the local instance?"
                )
                if update:
                    return ApplyResult(True, remote_instance)
                bprint(
                    f"\nYou are about to override the remote {model_name} "
                    f"with your local {model_name}:"
                )
                print(local_dict)
                update = typer.confirm("Are you sure?")
                if update:
                    local_instance = model.parse_obj(local_dict)
                    local_instance.save()
                    return ApplyResult(True, to_dict(local_instance))
                return ApplyResult(False, None)
            bprint(
                f"Nothing to update, the same {model_name} was found "
                "remotely"
            )
            return ApplyResult(False, None)
        bprint(f"\nThe following {model_name} was not found remotely")
        print(local_dict)
        self._remove_ids(model_name, local_dict)
        bprint(f"\nYou are about to create the following {model_name}:")
        print(local_dict)
        create = typer.confirm("Are you sure?")
        if create:
            local_instance = model.parse_obj(local_dict)
            local_instance.save()
            remote_instance = model.retrieve(resource_id=local_instance.id)
            return ApplyResult(True, to_dict(remote_instance))
        return ApplyResult(False, None)

    def _remove_ids(self, model_name, local_dict):
        if model_name == Asset.__class__.__name__:
            local_dict["id"] = None
            for attr in local_dict["attributes"]:
                attr["id"] = None
        else:
            local_dict["id"] = None
