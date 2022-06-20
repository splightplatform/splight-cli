import enum
import os, sys
import importlib
import subprocess
import logging
from pydantic import BaseModel, validator
from functools import cached_property
from tempfile import NamedTemporaryFile
from typing import Type, List, Union
from ..utils import *
from cli.settings import *

logger = logging.getLogger()

class ComponentAlreadyExistsException(Exception):
    pass

class Parameter(BaseModel):
    name: str
    type: str
    required: bool
    multiple: bool = False
    value: Union[str, int, float, bool, UUID, list, None]

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
        if VALID_PARAMETER_VALUES[type_] is None:
            if v is not None:
                raise ValueError(f"value must be None")
        else:
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

class Component:
    name = None
    type = None
    version = None
    parameters = None

    def __init__(self, path, context):
        logger.setLevel(logging.WARNING)
        self.path = validate_path_isdir(os.path.abspath(path))
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
            return importlib.import_module(component_directory_name)
        except Exception as e:
            raise Exception(f"Failed importing component {component_directory_name}: {str(e)}")

    def _validate_component(self):
        Spec(**self.spec)
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
            Spec(**self.spec)
        else:
            self.component = self._import_component()
            self._validate_component()

        self.name = self.spec["name"]
        self.version = self.spec["version"]
        self.parameters = self.spec["parameters"]
    
    def _load_vars_from_file(self):
        vars_file = os.path.join(self.path, VARS_FILE)
        if not os.path.isfile(vars_file):
            return
        vars = get_yaml_from_file(vars_file)
        for i, param in enumerate(self.spec["parameters"]):
            name = param["name"]
            if name in vars:
                self.spec["parameters"][i]["value"] = vars[name]

    def _prompt_null_parameters(self):
        for i, param in enumerate(self.spec["parameters"]):
            if param["value"] is None or param["value"] == []:
                self.spec["parameters"][i]["value"] = input_multiple(param) if param["multiple"] else input_single(param)
    
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

    def initialize(self):
        health_file = NamedTemporaryFile(prefix="healthy_")
        logger.debug(f"Created healthy file")
        command_prefixes_map =  {
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

        Spec(name=name, version=version, parameters=[])

        self.path = os.path.join(self.path, f"{name}-{version}")
        os.mkdir(self.path)

        for file_name in REQUIRED_FILES:
            template_name = file_name
            if file_name == COMPONENT_FILE:
                template_name = f"{type}.py"
            template: Template = get_template(template_name)
            file = template.render(
                component_type=type,
                component_name=name,
                version=version
            )
            file_path = os.path.join(self.path, file_name)
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
            

    def run(self, type, run_spec):
        logger.setLevel(logging.DEBUG)
        self._validate_type(type)
        self.spec = json.loads(run_spec)
        self._validate_component_structure()
        self._load_component_in_run()

        component_class = getattr(self.component, MAIN_CLASS_NAME)
        instance_id = self.spec['external_id']
        namespace = self.spec['namespace']
        component_class(
            instance_id=instance_id,
            namespace=namespace,
            run_spec=run_spec
        )

    def test(self, type):
        logger.setLevel(logging.DEBUG)
        self._validate_type(type)
        #type = type.capitalize()
        self._validate_component_structure()
        # self.initialize()
        self._load_component_in_push(no_import=False)
        self._load_vars_from_file()
        # self._prompt_null_parameters()
        component_class = getattr(self.component, MAIN_CLASS_NAME)
        instance_id = "db530a08-5973-4c65-92e8-cbc1d645ebb4"
        namespace = 'default'
        self.spec['type'] = type
        self.spec['external_id'] = instance_id
        self.spec['namespace'] = namespace
        run_spec_str: str = json.dumps(self.spec)
        component_class(
            instance_id=instance_id, # Why we need this if we are overriding it?
            namespace=namespace, # Why we need this?
            run_spec=run_spec_str
        )