import os, sys
import shutil
import importlib
import subprocess
import logging
from pydantic import BaseModel, validator
from functools import cached_property
from tempfile import NamedTemporaryFile
from typing import Type, List, Union
from .utils import *
from .storage import *
from .settings import *


logger = logging.getLogger()


class Parameter(BaseModel):
    name: str
    type: str
    required: bool
    value: Union[str, int, float, bool, UUID]

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
        try:
            v = VALID_PARAMETER_VALUES[type_](v)            
        except Exception:
            raise ValueError(f"value must be of type {VALID_PARAMETER_VALUES[type_].__name__}")
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

class Component:
    name = None
    type = None
    version = None
    parameters = None
    storage_client = None

    def __init__(self, path):
        self.path = validate_path_isdir(os.path.abspath(path))
    
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

    def _load_component(self) -> None:
        self.component = self._import_component()
        # DO NOT VALIDATE RUN SPEC SO FAR
        #self._validate_component()
        self.name, self.version = self.spec["version"].split("-")
        self.parameters = self.spec["parameters"]
    
    def _get_command_list(self) -> List[str]:
        initialization_file_path = os.path.join(self.path, INIT_FILE)
        lines: List[str] = []
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
        output = subprocess.check_output("ls /tmp/", shell=True)
        logger.debug(f"ls /tmp = {output}")
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

    def push(self, type):
        self._validate_type(type)
        self._validate_component_structure()
        self._load_component()
        self.storage_client = S3HubClient()
        versioned_name = f"{self.name}-{self.version}"
        self.storage_client.save_component(type, versioned_name, self.path)

    def pull(self, name, type, version):
        self._validate_type(type)

        Spec(name=name, version=version, parameters=[])

        versioned_name = f"{name}-{version}"
        component_path = os.path.join(self.path, versioned_name)

        if os.path.exists(component_path):
            raise Exception(f"Directory with name {versioned_name} already exists in path")

        self.storage_client = S3HubClient()

        if not self.storage_client.exists_in_hub(type, versioned_name):
            raise Exception(f"Component {versioned_name} does not exist in Splight Hub")
        
        os.mkdir(component_path)
        try:
            # Download zip
            self.storage_client.download_dir(type, versioned_name, self.path)
            # Download raw
            #self.storage_client.download_dir_raw(versioned_name, f"{type}/{versioned_name}", self.path)
        except:
            shutil.rmtree(component_path)
            raise

    def run(self, type, run_spec):
        self._validate_type(type)
        self.spec = json.loads(run_spec)
        self._validate_component_structure()
        self.initialize()
        self._load_component()

        component_class = getattr(self.component, MAIN_CLASS_NAME)
        instance_id = self.spec['external_id']
        namespace = self.spec['namespace']
        component_class(
            instance_id=instance_id,
            namespace=namespace,
            run_spec=run_spec
        )

    def test(self, type):
        self._validate_type(type)
        self._validate_component_structure()
        self.initialize()
        self._load_component()
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