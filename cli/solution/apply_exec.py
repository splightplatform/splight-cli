from collections import namedtuple

import typer
from deepdiff import DeepDiff
from rich import print
from splight_lib.models import Asset

from cli.solution.utils import (
    SplightTypes,
    StrKeyDict,
    bprint,
    parse_str_data_addr,
    to_dict,
)

ApplyResult = namedtuple("ApplyResult", ("update", "updated_dict"))


class ApplyExecutor:
    def __init__(self, state: StrKeyDict, regex_to_exclude: StrKeyDict):
        self._state = state
        self._model_to_regex = regex_to_exclude

    def apply(
        self, model: SplightTypes, local_dict: StrKeyDict
    ) -> ApplyResult:
        """Applies changes to the remote engine if needed.

        Parameters
        ----------
        model : SplightTypes
            A Splight model.
        local_dict : StrKeyDict
            Instance to be saved (or not) as a dictionary.

        Returns
        -------
        ApplyResult
            Named tuple containing the result of the apply step.
        """
        model_name = model.__name__
        instance_id = local_dict.get("id", None)

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

    def replace_data_addr(self):
        state_components = self._state["solution"]["components"]
        for i in range(len(state_components)):
            routines = state_components[i].get("routines", [])
            for routine in routines:
                self._replace_routine_data_addr(routine)

    def _replace_routine_data_addr(self, routine: StrKeyDict):
        for io_elem in routine["input"] + routine["output"]:
            if io_elem.get("value", None) is not None:
                io_elem["value"] = self._get_new_value(io_elem)

    def _get_new_value(self, io_elem):
        multiple = io_elem.get("multiple", False)
        if not multiple and isinstance(io_elem["value"], list):
            raise ValueError(
                f"Passed 'multiple: False' but value of {io_elem['name']} is "
                "a list. Aborted."
            )
        if multiple:
            return [self._parse_data_addr(da) for da in io_elem["value"]]
        else:
            return self._parse_data_addr(io_elem["value"])

    def _parse_data_addr(self, data_addr):
        result = parse_str_data_addr(data_addr)
        if result.is_id:
            return {"asset": result.asset, "attribute": result.attribute}
        state_assets = self._state["solution"]["assets"]
        for asset in state_assets:
            if asset["name"] == result.asset:
                asset_id = asset["id"]
                for attr in asset["attributes"]:
                    if attr["name"] == result.attribute:
                        attr_id = attr["id"]
                        break
                break
        return {"asset": asset_id, "attribute": attr_id}

    def _compare_with_remote(
        self, model: SplightTypes, local_dict: StrKeyDict
    ) -> ApplyResult:
        """Compares the local instance with the remote instances if any.

        Parameters
        ----------
        model : SplightTypes
            A Splight model.
        local_dict : StrKeyDict
            Instance to be saved (or not) as a dictionary.

        Returns
        -------
        ApplyResult
            Named tuple containing the result of the apply step.
        """
        model_name = model.__name__
        instance_id = local_dict["id"]

        remote_list = model.list(id__in=instance_id)
        if remote_list:
            remote_instance = to_dict(remote_list[0])
            exclude_regex = self._model_to_regex.get(model_name, None)
            diff = DeepDiff(
                local_dict,
                remote_instance,
                exclude_regex_paths=exclude_regex,
            )
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
        if model_name == Asset.__name__:
            local_dict["id"] = None
            for attr in local_dict["attributes"]:
                attr["id"] = None
        else:
            local_dict["id"] = None
