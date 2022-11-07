import os
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import click

from cli.component.handler import ComponentHandler
from cli.constants import (
    DEFAULT_NAMESPACE,
)
from cli.utils import (
    get_yaml_from_file,
    input_single,
    save_yaml_to_file,
)


class InvalidComponentID(Exception):
    pass


class ComponentConfigLoader:

    _EXTRA_SPEC_FIELDS = ["namespace", "type"]

    def __init__(
        self,
        context,
        vars_file_path: str,
        component_type: str,
        reset_values: bool = False,
    ):
        self._context = context
        self._vars_file_path = vars_file_path
        self._reset = reset_values
        self._component_type = component_type

        if not os.path.exists(self._vars_file_path):
            Path(self._vars_file_path).touch()

    def load_values(self, spec_dict: Dict) -> Dict:
        variables = get_yaml_from_file(self._vars_file_path)

        full_spec = {}
        full_spec["type"] = self._component_type.title()
        full_spec["namespace"] = DEFAULT_NAMESPACE

        replaced_input = self._replace_input_values(spec_dict, variables)
        spec_dict["input"] = replaced_input
        full_spec.update(spec_dict)
        if self._reset:
            full_spec = self._reset_all_values(full_spec)

        # CHECK INPUT WITH NONE VALUES
        full_spec = self._fill_missing_parameter(full_spec)
        self._export_to_yaml(full_spec)
        return full_spec

    def _reset_all_values(self, spec: Dict) -> Dict:
        simple_params, custom_params = self._split_custom_params(spec)

        reseted_input = []
        for param in simple_params:
            param["value"] = input_single(param)
            reseted_input.append(param)

        for param in custom_params:
            param_name = param["name"]
            param_values = param["value"]
            if param["multiple"]:
                new_value = self._read_multiple_custom_type(
                    param_name, param_values
                )
            else:
                new_value = self._read_single_custom_type(
                    param_name, param_values
                )
            param["value"] = new_value

        reseted_input.extend(custom_params)
        spec["input"] = reseted_input
        return spec

    def _fill_missing_parameter(self, spec: Dict) -> Dict:
        simple_params, custom_params = self._split_custom_params(spec)
        simple_params = self._fill_missing_simple_input(simple_params)

        spec["input"] = simple_params
        spec["input"].extend(custom_params)

        for param in custom_params:
            param_value = param["value"]
            if param["multiple"]:
                values = []
                for item in param_value:
                    values.append(self._fill_missing_simple_input(
                        item, name_prefix=param["name"]
                    ))
            else:
                param["values"] = self._fill_missing_simple_input(
                    param_value, name_prefix=param["name"]
                )

        return spec

    def _fill_missing_simple_input(
        self, parameters: List[Dict], name_prefix: Optional[str] = None
    ) -> List[Dict]:
        for param in parameters:
            param_value = param.get("value")
            param_value = (
                param_value[0]
                if isinstance(param_value, list)
                else param_value
            )
            if not param_value:
                param_name = param["name"]
                param["name"] = (
                    f"{name_prefix}.{param_name}"
                    if name_prefix
                    else param_name
                )
                param["value"] = input_single(param)
                param["name"] = param_name
        return parameters

    def _replace_input_values(
        self,
        spec_dict: Dict,
        variables: Dict,
    ) -> Dict:
        replaced = []

        simple_params, custom_params = self._split_custom_params(spec_dict)
        for param in simple_params:
            param["value"] = variables.get(param["name"], param["value"])
            replaced.append(param)

        ct_def = spec_dict["custom_types"]
        for param in custom_params:
            prefix = param["name"]
            param_type = param["type"]
            param_values = param["value"]
            if param["multiple"]:
                definition = [ct for ct in ct_def if ct["name"] == param_type]
                fields = definition[0]["fields"]
                param_vars = variables.get(prefix, [])
                sub_param_items = [
                    deepcopy(fields) for _ in range(len(param_vars))
                ]
                for idx, item in enumerate(sub_param_items):
                    for sub_param in item:
                        sub_param["value"] = param_vars[idx][sub_param["name"]]
                param["value"] = (
                    sub_param_items if sub_param_items else param_values
                )
            else:
                for sub_param in param_values:
                    value = variables.get(prefix, {}).get(sub_param["name"])
                    sub_param["value"] = (
                        value if value else sub_param.get("value")
                    )
            replaced.append(param)

        return replaced

    def _read_multiple_custom_type(
        self, param_name: str, childs_params: List[Dict]
    ) -> List[List[Dict]]:
        template = deepcopy(childs_params[0])
        replaced_childs = []

        # Modify previous values
        to_delete = []
        for param in childs_params:
            action = click.prompt(
                f"Do you want to modify (m) or delete (d) the value {param}",
                type=str,
                default="n"
            )
            if action in ["d", "D"]:
                to_delete.append(param)
            elif action in ["m", "M"]:
                param = self._read_single_custom_type(
                    param_name, param
                )
                replaced_childs.append(param)
            else:
                replaced_childs.append(param)

        for item in to_delete:
            childs_params.remove(item)

        # Adds new values if is needed
        while True:
            add_new = click.prompt(
                f"Do you want to add new item in variable {param_name}? (y/n)",
                type=str,
                default="n"
            )
            if add_new not in ["y", "Y"]:
                break
            new_item = self._read_single_custom_type(
                param_name, template
            )
            replaced_childs.append(new_item)

        if not len(replaced_childs):
            raise ValueError(
                f"Should be at least one element for {param_name}"
            )
        return replaced_childs

    def _read_single_custom_type(
        self, param_name: str, childs_params: List[Dict]
    ) -> List[Dict]:
        replaced_childs = []
        for param in childs_params:
            name = param["name"]
            to_replace = param
            to_replace["name"] = f"{param_name}.{name}"
            new_value = input_single(to_replace)
            param["value"] = new_value
            param["name"] = name
            replaced_childs.append(param)

        return replaced_childs

    def _export_to_yaml(self, spec_dict: Dict):
        vars = {key: spec_dict.get(key) for key in self._EXTRA_SPEC_FIELDS}
        custom_types = [x["name"] for x in spec_dict["custom_types"]]

        for input_param in spec_dict["input"]:
            param_name = input_param["name"]
            param_type = input_param["type"]
            param_value = input_param["value"]
            if param_type in custom_types:
                if input_param["multiple"]:
                    var_value = []
                    for item in param_value:
                        var_value.append(
                            {var["name"]: var.get("value") for var in item}
                        )
                else:
                    var_value = {
                        var["name"]: var["value"] for var in param_value
                    }
            else:
                var_value = param_value
            vars[param_name] = var_value

        save_yaml_to_file(payload=vars, file_path=self._vars_file_path)

    @staticmethod
    def _split_custom_params(spec_dict: Dict) -> Tuple[List, List]:
        custom_types_names = [
            param["name"] for param in spec_dict["custom_types"]
        ]
        input_parameters = spec_dict.get("input", [])
        custom_params = [
            param
            for param in input_parameters
            if param["type"] in custom_types_names
        ]
        simple_params = [
            param
            for param in input_parameters
            if param["type"] not in custom_types_names
        ]
        return simple_params, custom_params

    @staticmethod
    def _read_single_str(name: str, default: Optional[Any]) -> str:
        param = {
            "name": name,
            "value": default,
            "type": "str",
            "multiple": False,
            "required": True,
        }
        value = input_single(param)
        return value

    def _create_new_component(self, name: str, version: str) -> str:
        handler = ComponentHandler(self._context)
        component = handler.create_component(
            component_type=self._component_type,
            component_name=name,
            component_version=version
        )
        return component["id"]
