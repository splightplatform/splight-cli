from splight_lib.component import AbstractComponent
from typing import Type, List
from pathlib import Path
from cli.settings import *
from cli.constants import *
from cli.utils import *
from cli.component.handler import ComponentHandler, UserHandler
from ..utils import *
from .deployment import Deployment
from typing import Type, List, Union
from tempfile import NamedTemporaryFile
import importlib
import json
import logging
import os
import subprocess
import sys
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import List, Type, Union, Optional

import click
from jinja2 import Template
from typing import Type, List, Union
from cli.component.handler import ComponentHandler, UserHandler
from cli.utils import *
from cli.constants import *
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Type, List, Union
from ..utils import *
from cli.settings import *
from splight_lib.component import AbstractComponent
from splight_lib import logging
from cli.component.exception import InvalidComponentType
from cli.component.handler import ComponentHandler, UserHandler


from cli.constants import (
    COMPONENT_FILE,
    DEFAULT_EXTERNAL_ID,
    DEFAULT_NAMESPACE,
    INIT_FILE,
    MAIN_CLASS_NAME,
    PICTURE_FILE,
    REQUIRED_FILES,
    SPEC_FILE,
    VALID_PARAMETER_VALUES,
    VALID_TYPES,
    VARS_FILE,
)
from cli.utils import (
    api_get,
    get_json_from_file,
    get_template,
    get_yaml_from_file,
    input_single,
    save_yaml_to_file,
    validate_path_isdir,
)


logger = logging.getLogger()


class ComponentAlreadyExistsException(Exception):
    pass


class Component:
    name = None
    type = None
    version = None
    parameters = None

    def __init__(self, path, context):
        self.path = validate_path_isdir(os.path.abspath(path))
        self.vars_file = os.path.join(self.path, VARS_FILE)
        self.spec_file = os.path.join(self.path, SPEC_FILE)
        self.context = context

    def _validate_component_structure(self):
        validate_path_isdir(self.path)
        for required_file in REQUIRED_FILES:
            if not os.path.isfile(os.path.join(self.path, required_file)):
                raise Exception(
                    f"{required_file} file is missing in {self.path}"
                )

    def _validate_component(self):
        try:
            Deployment.verify(self.spec)
            component_name = MAIN_CLASS_NAME
            if not hasattr(self.component, component_name):
                raise Exception(
                    f"Component does not have a class called {component_name}"
                )

            component_class = getattr(self.component, component_name)
            if not isinstance(component_class, Type):
                raise Exception(
                    f"There's no component class called {component_name}"
                )

        except Exception as e:
            raise Exception(f"Failed to validate component: {str(e)}")

    @staticmethod
    def _validate_type(type: str) -> str:
        if type.title() not in VALID_TYPES:
            raise InvalidComponentType(f"Invalid component type: {type}")
        # Return value in lower case
        return type.lower()

    def _load_component(self) -> None:
        self.component = self._import_component()
        self._validate_component()

    def _load_component_in_push(self, no_import) -> None:
        if no_import:
            self.component = None
            Deployment.verify(self.spec)
        else:
            self.component = self._import_component()
            self._validate_component()

    def _load_spec(self):
        self.spec = get_json_from_file(self.spec_file)
        self.name = self.spec["name"]
        self.version = self.spec["version"]

    def _load_run_spec_fields(self, extra_run_spec_fields):
        vars = get_yaml_from_file(self.vars_file)
        for i, param in enumerate(self.spec["input"]):
            name = param["name"]
            if name in vars:
                self.run_spec["input"][i]["value"] = vars[name]
        for key in extra_run_spec_fields.keys():
            self.run_spec[key] = vars[key]

    def _prompt_run_spec_fields(
        self, reset_input, extra_run_spec_fields: dict
    ):
        Path(self.vars_file).touch()
        vars = get_yaml_from_file(self.vars_file)
        for i, param in enumerate(self.spec["input"]):
            name = param["name"]
            if reset_input or name not in vars:
                param["value"] = vars.get(name, param["value"])
                if param["type"] not in VALID_PARAMETER_VALUES:
                    raise Exception(f"Invalid parameter type: {param['type']}."
                                    f" Custom types not supported yet.")
                param['value'] = vars.get(name, param['value'])
                vars[name] = input_single(param)
                if param.get("multiple", False) and vars[name]:
                    vars[name] = vars[name].split(",")
        for key, default in extra_run_spec_fields.items():
            if reset_input or key not in vars:
                vars[key] = click.prompt(
                    key, type=str, default=default, show_default=True
                )
        save_yaml_to_file(payload=vars, file_path=self.vars_file)

    def _command_run(self, command: List[str]) -> None:
        command: str = " ".join(command)
        logger.debug(f"Running initialization command: {command} ...")
        try:
            subprocess.run(command, check=True, cwd=self.path, shell=True)
        except subprocess.CalledProcessError as e:
            raise Exception(
                f"Failed to run command: {e.cmd}. Output: {e.output}"
            )

    def _get_command_list(self) -> List[str]:
        initialization_file_path = os.path.join(self.path, INIT_FILE)
        lines: List[str] = []
        lines.append(["RUN", "pip", "cache", "purge"])
        with open(initialization_file_path) as f:
            for line in f:
                line = line.strip()
                if line.startswith("#") or line == "":
                    continue
                lines.append(line.split(" "))
        return lines

    def _get_random_picture(self, path):
        # TODO REMOVE THIS.. MOVE TO HUBCLIENT IMPLEMENTATION
        user_handler = UserHandler(self.context)
        file_data = api_get(
            f"{self.context.workspace.settings.SPLIGHT_HUB_API_HOST}/random_picture/",
            headers=user_handler.authorization_header,
        )
        with open(path, "wb+") as f:
            f.write(file_data.content)

    def _import_component(self):
        component_directory_name = self.path.split(os.sep)[-1]
        sys.path.append(os.path.dirname(self.path))
        try:
            component = importlib.import_module(component_directory_name)
            main_class = getattr(component, MAIN_CLASS_NAME)
            if not any(
                [
                    parent_class.__name__ == AbstractComponent.__name__
                    for parent_class in main_class.__mro__
                ]
            ):
                raise Exception(
                    f"Component class {MAIN_CLASS_NAME} must inherit from one of Splight's component classes"
                )
            return component
        except Exception as e:
            raise Exception(
                f"Failed importing component {component_directory_name}: {str(e)}"
            )

    def initialize(self):
        # TODO this should be removed from here. But it is present
        # to avoid to fail redinessprobe during req installation
        health_file = NamedTemporaryFile(prefix="healthy_")
        logger.debug("Created healthy file")
        command_prefixes_map = {
            "RUN": self._command_run,
        }

        try:
            for command in self._get_command_list():
                prefix: str = command[0]

                if prefix not in command_prefixes_map.keys():
                    raise Exception(f"Invalid command: {command[0]}")

                command_prefixes_map[prefix](command[1:])

        except Exception as e:
            health_file.close()
            raise e

    @classmethod
    def list(cls, context, type):
        component_type = cls._validate_type(type)
        handler = ComponentHandler(context)
        return handler.list_components(component_type)

    def create(self, name, type, version):
        component_type = self._validate_type(type)

        self._validate_type(type)
        Deployment.verify({
            "name": name,
            "version": version,
            "custom_types": [],
            "input": [],
            "output": [],
            "filters": []
        })

        self.path = os.path.join(self.path, f"{name}-{version}")
        os.mkdir(self.path)

        for file_name in REQUIRED_FILES:
            template_name = file_name
            file_path = os.path.join(self.path, file_name)
            if file_name == PICTURE_FILE:
                self._get_random_picture(file_path)
                continue
            if file_name == COMPONENT_FILE:
                template_name = f"{component_type}.py"
            template: Template = get_template(template_name)
            file = template.render(
                component_type=type, component_name=name, version=version
            )
            with open(file_path, "w+") as f:
                f.write(file)

    def push(self, type, force, public):
        component_type = self._validate_type(type)
        self._validate_component_structure()
        self._load_spec()  # TODO spec should have public attr
        self._load_component()

        handler = ComponentHandler(self.context)
        if not force and handler.exists_in_hub(
            component_type, self.name, self.version
        ):
            raise ComponentAlreadyExistsException
        handler.upload_component(
            component_type,
            self.name,
            self.version,
            self.parameters,
            self.tags,
            public,
            self.path,
        )

    def pull(self, name, type, version):
        component_type = self._validate_type(type)

        versioned_name = f"{name}-{version}"
        component_path = os.path.join(self.path, versioned_name)

        if os.path.exists(component_path):
            raise Exception(
                f"Directory with name {versioned_name} already exists in path"
            )

        handler = ComponentHandler(self.context)
        if not handler.exists_in_hub(component_type, name, version):
            raise Exception(
                f"Component {versioned_name} does not exist in Splight Hub"
            )

        handler.download_component(component_type, name, version, self.path)

    def delete(self, name, type, version):
        component_type = self._validate_type(type)

        versioned_name = f"{name}-{version}"

        handler = ComponentHandler(self.context)
        if not handler.exists_in_hub(component_type, name, version):
            raise Exception(
                f"Component {versioned_name} does not exist in Splight Hub"
            )

        handler.delete_component(component_type, name, version)

    def run(self, type, run_spec, reset_input):
        component_type = self._validate_type(type)
        self._validate_type(type)
        self._validate_component_structure()
        self._load_spec()

        extra_run_spec_fields = {
            "namespace": DEFAULT_NAMESPACE,
            "external_id": DEFAULT_EXTERNAL_ID,
            "type": component_type.title(),
        }
        if run_spec:
            self.run_spec = json.loads(run_spec)
        else:
            self.run_spec = self.spec
            self._prompt_run_spec_fields(
                extra_run_spec_fields=extra_run_spec_fields,
                reset_input=reset_input,
            )
            self._load_run_spec_fields(extra_run_spec_fields)
        self._load_component()

        component_class = getattr(self.component, MAIN_CLASS_NAME)
        component = component_class(
            run_spec=self.run_spec,
            initial_setup=self.context.workspace.settings.dict()
        )
        component.start()
