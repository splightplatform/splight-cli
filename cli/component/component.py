import os
import sys
import importlib
import subprocess
import logging
from pathlib import Path
from functools import cached_property
from tempfile import NamedTemporaryFile
from typing import Type, List, Union, Optional
from ..utils import *
from cli.settings import *
from splight_lib.component import AbstractComponent
from .description_spec import DescriptionSpec
from .input_spec import InputSpecFactory
logger = logging.getLogger()


class ComponentAlreadyExistsException(Exception):
    pass


class Component:
    name = None
    type = None
    version = None
    parameters = None

    def __init__(self, path, context):
        logger.setLevel(logging.WARNING)
        self.path = validate_path_isdir(os.path.abspath(path))
        self.vars_file = os.path.join(self.path, VARS_FILE)
        Path(self.vars_file).touch()
        self.context = context

    @cached_property
    def spec(self) -> dict:
        return get_json_from_file(os.path.join(self.path, SPEC_FILE))

    def _validate_component_structure(self):
        validate_path_isdir(self.path)
        for required_file in REQUIRED_FILES:
            if not os.path.isfile(os.path.join(self.path, required_file)):
                raise Exception(f"{required_file} file is missing in {self.path}")

    def _import_component(self):
        component_directory_name = self.path.split(os.sep)[-1]
        sys.path.append(os.path.dirname(self.path))
        try:
            component = importlib.import_module(component_directory_name)
            main_class = getattr(component, MAIN_CLASS_NAME)
            if not any([parent_class.__name__ == AbstractComponent.__name__ for parent_class in main_class.__mro__]):
                raise Exception(f"Component class {MAIN_CLASS_NAME} must inherit from one of Splight's component classes")
            return component
        except Exception as e:
            raise Exception(f"Failed importing component {component_directory_name}: {str(e)}")

    def _validate_component(self):
        DescriptionSpec(**self.spec)
        try:
            component_name = MAIN_CLASS_NAME
            if not hasattr(self.component, component_name):
                raise Exception(f"Component does not have a class called {component_name}")

            component_class = getattr(self.component, component_name)
            if not isinstance(component_class, Type):
                raise Exception(f"There's no component class called {component_name}")

        except Exception as e:
            raise Exception(f"Failed to validate component: {str(e)}")

    def _validate_type(self, type) -> None:
        if type not in VALID_TYPES:
            raise Exception(f"Invalid component type: {type}")
        return type

    def _load_component_in_run(self) -> None:
        self.component = self._import_component()
        self.name, self.version = self.spec["version"].split("-")
        self.parameters = self.spec["parameters"]

    def _load_component_in_push(self, no_import) -> None:
        if no_import:
            self.component = None
            DescriptionSpec(**self.spec)
        else:
            self.component = self._import_component()
            self._validate_component()

        self.name = self.spec["name"]
        self.version = self.spec["version"]
        self.parameters = self.spec["parameters"]

    def _prompt_parameters(self, reset_input):
        vars = get_yaml_from_file(self.vars_file)
        for i, param in enumerate(self.spec["parameters"]):
            name = param["name"]
            if reset_input or name not in vars:
                param['value'] = vars.get(name, param['value'])
                vars[name] = input_single(param)
                if param.get("multiple", False) and vars[name]:
                    vars[name] = vars[name].split(',')
        save_yaml_to_file(payload=vars, file_path=self.vars_file)

    def _load_vars_from_file(self):
        vars = get_yaml_from_file(self.vars_file)
        for i, param in enumerate(self.spec["parameters"]):
            name = param["name"]
            if name in vars:
                self.spec["parameters"][i]["value"] = vars[name]

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

    def _command_run(self, command: List[str]) -> None:
        command: str = " ".join(command)
        logger.debug(f"Running initialization command: {command} ...")
        try:
            subprocess.run(command, check=True, cwd=self.path, shell=True)
        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to run command: {e.cmd}. Output: {e.output}")

    def _get_random_picture(self, path):
        user_handler = UserHandler(self.context)
        file_data = api_get(f"{self.context.SPLIGHT_HUB_API_HOST}/random_picture/", headers=user_handler.authorization_header)
        with open(path, "wb+") as f:
            f.write(file_data.content)

    def initialize(self):
        health_file = NamedTemporaryFile(prefix="healthy_")
        logger.debug(f"Created healthy file")
        command_prefixes_map = {
            "RUN": self. _command_run,
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

    def create(self, name, type, version):
        self._validate_type(type)

        DescriptionSpec(name=name, version=version, parameters=[])

        self.path = os.path.join(self.path, f"{name}-{version}")
        os.mkdir(self.path)

        for file_name in REQUIRED_FILES:
            template_name = file_name
            file_path = os.path.join(self.path, file_name)
            if file_name == PICTURE_FILE:
                self._get_random_picture(file_path)
                continue
            if file_name == COMPONENT_FILE:
                template_name = f"{type}.py"
            template: Template = get_template(template_name)
            file = template.render(
                component_type=type,
                component_name=name,
                version=version
            )
            with open(file_path, "w+") as f:
                f.write(file)

    def push(self, type, force, no_import):
        self.type = self._validate_type(type)
        self._validate_component_structure()
        self._load_component_in_push(no_import)

        handler = ComponentHandler(self.context)
        if not force and handler.exists_in_hub(self.type, self.name, self.version):
            raise ComponentAlreadyExistsException
        handler.upload_component(self.type, self.name, self.version, self.parameters, self.path)

    def pull(self, name, type, version):
        self._validate_type(type)

        versioned_name = f"{name}-{version}"
        component_path = os.path.join(self.path, versioned_name)

        if os.path.exists(component_path):
            raise Exception(f"Directory with name {versioned_name} already exists in path")

        handler = ComponentHandler(self.context)
        if not handler.exists_in_hub(type, name, version):
            raise Exception(f"Component {versioned_name} does not exist in Splight Hub")

        handler.download_component(type, name, version, self.path)

    def delete(self, name, type, version):
        self._validate_type(type)

        versioned_name = f"{name}-{version}"

        handler = ComponentHandler(self.context)
        if not handler.exists_in_hub(type, name, version):
            raise Exception(f"Component {versioned_name} does not exist in Splight Hub")

        handler.delete_component(type, name, version)

    def run(self, type, run_spec):
        logger.setLevel(logging.DEBUG)
        self._validate_type(type)
        expected_structure = DescriptionSpec(**self.spec)
        self.spec = json.loads(run_spec)
        self._validate_component_structure()
        self._load_component_in_run()

        component_class = getattr(self.component, MAIN_CLASS_NAME)
        instance_id = self.spec['external_id']
        namespace = self.spec['namespace']

        input_spec_factory = InputSpecFactory(expected_structure)

        component_class(
            instance_id=instance_id,
            namespace=namespace,
            run_spec=input_spec_factory.get_input_spec(self.spec)
        )

    def test(self, type, namespace, instance_id, reset_input):
        logger.setLevel(logging.DEBUG)
        self._validate_type(type)
        expected_structure = DescriptionSpec(**self.spec)
        self._validate_component_structure()
        self._load_component_in_push(no_import=False)
        self._prompt_parameters(reset_input=reset_input)
        self._load_vars_from_file()
        component_class = getattr(self.component, MAIN_CLASS_NAME)
        self.spec['type'] = type
        self.spec['external_id'] = instance_id if instance_id else "db530a08-5973-4c65-92e8-cbc1d645ebb4"
        self.spec['namespace'] = namespace if namespace is not None else 'default'
        input_spec_factory = InputSpecFactory(expected_structure)

        component_class(
            instance_id=self.spec['external_id'],  # Why we need this if we are overriding it?
            namespace=self.spec['namespace'],
            run_spec=input_spec_factory.get_input_spec(self.spec)
        )
