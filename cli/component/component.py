import os
import sys
import importlib
import subprocess
import logging
from pydantic import BaseModel, validator
from tempfile import NamedTemporaryFile
from typing import Type, List, Union
from cli.component.handler import ComponentHandler, UserHandler
from cli.utils import *
from cli.constants import *
from splight_lib.component import AbstractComponent

logger = logging.getLogger()


class ComponentAlreadyExistsException(Exception):
    pass


class Parameter(BaseModel):
    name: str
    type: str
    required: bool
    multiple: bool = False
    value: Union[str, int, float, bool, list, None]

    @validator("type")
    def validate_type(cls, type):
        if type not in VALID_PARAMETER_VALUES:
            raise ValueError(f"type must be one of: {list(VALID_PARAMETER_VALUES.keys())}")
        return type

    @validator("value")
    def validate_value(cls, v, values, field):
        if "type" not in values:
            return values

        type_ = values["type"]
        if VALID_PARAMETER_VALUES[type_] is not None:
            if not values["multiple"]:
                try:
                    v = VALID_PARAMETER_VALUES[type_](v)
                except Exception:
                    if v is not None or values["required"]:
                        raise ValueError(f"value must be of type {str(VALID_PARAMETER_VALUES[type_])}")
            else:
                if not isinstance(v, list):
                    raise ValueError(f"value must be a list")
                try:
                    new_v = []
                    for v_ in v:
                        new_v.append(VALID_PARAMETER_VALUES[type_](v_))
                    v = new_v
                except Exception as e:
                    raise ValueError(f"the value in the list must be of type {str(VALID_PARAMETER_VALUES[type_])}")
        return v


class Spec(BaseModel):
    name: str
    version: str
    parameters: List[Parameter]

    @validator("name")
    def validate_name(cls, name):
        invalid_characters = ["/", "-"]
        if not name[0].isupper():
            raise ValueError(f"value's first letter must be capitalized")
        if any(x in name for x in invalid_characters):
            raise Exception(f"value cannot contain any of these characters: {invalid_characters}")
        return name

    @validator("version")
    def validate_version(cls, version):
        invalid_characters = ["/", "-"]
        if len(version) > 20:
            raise Exception(f"value must be 20 characters maximum")

        if any(x in version for x in invalid_characters):
            raise Exception(f"value cannot contain any of these characters: {invalid_characters}")
        return version

    @validator("parameters")
    def validate_parameters(cls, parameters):
        parameters_names = set()
        for parameter in parameters:
            parameter_name = parameter.name
            if parameter_name in parameters_names:
                raise Exception(f"Parameter name {parameter_name} is not unique")
            parameters_names.add(parameter_name)
        return parameters

    @classmethod
    def verify(cls, dict: dict):
        cls(**dict)


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
                raise Exception(f"{required_file} file is missing in {self.path}")

    def _validate_component(self):
        try:
            Spec.verify(self.spec)
            component_name = MAIN_CLASS_NAME
            if not hasattr(self.component, component_name):
                raise Exception(f"Component does not have a class called {component_name}")

            component_class = getattr(self.component, component_name)
            if not isinstance(component_class, Type):
                raise Exception(f"There's no component class called {component_name}")

        except Exception as e:
            raise Exception(f"Failed to validate component: {str(e)}")

    @staticmethod
    def _validate_type(type) -> None:
        if type not in VALID_TYPES:
            raise Exception(f"Invalid component type: {type}")
        return type

    def _load_component(self) -> None:
        self.component = self._import_component()
        self._validate_component()

    def _load_spec(self):
        self.spec = get_json_from_file(self.spec_file)
        self.name = self.spec["name"]
        self.version = self.spec["version"]
        self.parameters = self.spec["parameters"]

    def _load_run_spec_fields(self, extra_run_spec_fields):
        vars = get_yaml_from_file(self.vars_file)
        for i, param in enumerate(self.spec["parameters"]):
            name = param["name"]
            if name in vars:
                self.run_spec["parameters"][i]["value"] = vars[name]        
        for key in extra_run_spec_fields.keys():
            self.run_spec[key] = vars[key]

    def _prompt_run_spec_fields(self, reset_input, extra_run_spec_fields: dict):
        Path(self.vars_file).touch()
        vars = get_yaml_from_file(self.vars_file)
        for i, param in enumerate(self.spec["parameters"]):
            name = param["name"]
            if reset_input or name not in vars:
                param['value'] = vars.get(name, param['value'])
                vars[name] = input_single(param)
                if param.get("multiple", False) and vars[name]:
                    vars[name] = vars[name].split(',')
        for key, default in extra_run_spec_fields.items():
            if reset_input or key not in vars:
                vars[key] = click.prompt(
                    key,
                    type=str,
                    default=default,
                    show_default=True
                )
        save_yaml_to_file(payload=vars, file_path=self.vars_file)

    def _command_run(self, command: List[str]) -> None:
        command: str = " ".join(command)
        logger.debug(f"Running initialization command: {command} ...")
        try:
            subprocess.run(command, check=True, cwd=self.path, shell=True)
        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to run command: {e.cmd}. Output: {e.output}")

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
        file_data = api_get(f"{self.context.workspace.settings.SPLIGHT_HUB_API_HOST}/random_picture/", headers=user_handler.authorization_header)
        with open(path, "wb+") as f:
            f.write(file_data.content)

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

    def initialize(self):
        # TODO this should be removed from here. But it is present 
        # to avoid to fail redinessprobe during req installation
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

    @classmethod
    def list(cls, context, type):
        cls._validate_type(type)
        handler = ComponentHandler(context)
        return handler.list_components(type)

    def create(self, name, type, version):
        self._validate_type(type)

        Spec.validate({
            "name": name,
            "version": version,
            "parameters": []
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
                template_name = f"{type}.py"
            template: Template = get_template(template_name)
            file = template.render(
                component_type=type,
                component_name=name,
                version=version
            )
            with open(file_path, "w+") as f:
                f.write(file)

    def push(self, type, force, public):
        self._validate_type(type)
        self._validate_component_structure()
        self._load_spec() # TODO spec should have public attr
        self._load_component()

        handler = ComponentHandler(self.context)
        if not force and handler.exists_in_hub(type, self.name, self.version):
            raise ComponentAlreadyExistsException
        handler.upload_component(type, self.name, self.version, self.parameters, public, self.path)

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

    def run(self, type, run_spec, reset_input):
        self._validate_type(type)
        self._validate_component_structure()
        self._load_spec()

        extra_run_spec_fields = {
            'namespace': "DEFAULT_NAMESPACE",
            'external_id': "DEFAULT_EXT_ID",
            'type': type.title(),
        }
        if run_spec:
            self.run_spec = json.loads(run_spec)
        else:
            self.run_spec = self.spec
            self._prompt_run_spec_fields(
                extra_run_spec_fields=extra_run_spec_fields,
                reset_input=reset_input
            )
            self._load_run_spec_fields(extra_run_spec_fields)

        self._load_component()

        component_class = getattr(self.component, MAIN_CLASS_NAME)
        component = component_class(
            instance_id=self.run_spec['external_id'],
            namespace=self.run_spec['namespace'],
            run_spec=json.dumps(self.run_spec)
        )
        component.setup = self.context.workspace.settings.dict()
        component.start()
