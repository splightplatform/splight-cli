import os, sys
import requests
import shutil
import importlib
import zipfile
import subprocess
from typing import Type
from .utils import *
from .settings import API_URL


class Component:
    COMPONENT_FILE = "__init__.py"
    SPEC_FILE = "spec.json"
    INIT_FILE = "Initialization"
    README_FILE = "README.md"
    REQUIRED_FILES = [COMPONENT_FILE, SPEC_FILE, INIT_FILE, README_FILE]
    VALID_TYPES = ["algorithm", "io", "network", "io_client", "io_server"]
    VALID_PARAMETER_VALUES = {
        "str": str,
        "int": int,
        "float": float,
        "file": str
    }
    name = None
    type = None
    version = None
    parameters = None

    def __init__(self, path):
        self.path = validate_path_isdir(os.path.abspath(path))
        

    def _validate_component_structure(self):
        validate_path_isdir(self.path)
        for required_file in self.REQUIRED_FILES:
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
        try:
            for key in ["name", "version", "parameters"]:
                if key not in self.spec:
                    raise Exception(f"{key} is missing in {self.SPEC_FILE}")

            self.validate_name(self.spec["name"])
            self.validate_version(self.spec["version"])
            self.validate_parameters(self.spec["parameters"])

            component_name = "Main"
            if not hasattr(self.component, component_name):
                raise Exception(f"Component does not have a class called {component_name}")

            component_class = getattr(self.component, component_name)
            if not isinstance(component_class, Type):
                raise Exception(f"There's no component class called {component_name}")

        except Exception as e:
            raise Exception(f"Failed to validate component: {str(e)}")

    def validate_name(self, name) -> None:
        invalid_characters = ["/", "-"]
        if not isinstance(name, str):
            raise Exception(f"Component name must be a string")
        if not name[0].isupper():
            raise ValueError(f"Component name: {name} first letter must be capitalized")
        if any(x in name for x in invalid_characters):
            raise Exception(f"Component name cannot contain any of these characters: {invalid_characters}")
        return name

    def validate_type(self, type) -> None:
        if type not in self.VALID_TYPES:
            raise Exception(f"Invalid component type: {type}")
        return type

    def validate_version(self, version):
        invalid_characters = ["/", "-"]
        if not isinstance(version, str):
            raise Exception(f"Component version must be a string")
        if len(version) > 20:
            raise Exception(f"Component version must be 20 characters maximum")
        if any(x in version for x in invalid_characters):
            raise Exception(f"Component version cannot contain any of these characters: {invalid_characters}")
        return version

    def validate_parameters(self, parameters):
        if not isinstance(parameters, list):
            raise Exception(f"Component parameters must be a list")

        for parameter in parameters:
            if not isinstance(parameter, dict):
                raise Exception(f"Component parameter must be a dictionary")
            if "name" not in parameter:
                raise Exception(f"Component parameter must have a name")
            if "type" not in parameter:
                raise Exception(f"Component parameter must have a type")
            if "required" not in parameter:
                raise Exception(f"Component parameter must have a required value")
            if parameter["type"] not in self.VALID_PARAMETER_VALUES.keys():
                raise Exception(f"Component parameter type must be one of: {self.VALID_PARAMETER_VALUES.keys()}")
            if not isinstance(parameter["name"], str):
                raise Exception(f"Component parameter name must be a string")
            if not isinstance(parameter["required"], bool):
                raise Exception(f"Component parameter required must be a boolean")
        return parameters

    def _get_component_zip(self):
        shutil.make_archive(self.name, 'zip', self.path)
        file = {}
        zip_file = f"{self.name}.zip"
        with open(zip_file, 'rb') as f:
            file['file'] = f.read()
        os.remove(zip_file)
        return file

    def _load_component(self, type):
        self.type = self.validate_type(type)
        self._validate_component_structure()
        self.component = self._import_component()
        self.spec = get_json_from_file(os.path.join(self.path, self.SPEC_FILE))
        self._validate_component()
        self.name = self.spec["name"]
        self.version = self.spec["version"]
        self.parameters = self.spec["parameters"]

    def initialize(self):
        valid_command_prefixes = ["RUN"]
        initialization_file_path = os.path.join(self.path, self.INIT_FILE)
        with open(initialization_file_path) as f:
            for line in f:
                if line.startswith("#"):
                    continue
                command = line.split(" ")
                if command[0] not in valid_command_prefixes:
                    raise Exception(f"Invalid command: {command[0]}")
                if command[0] == "RUN":
                    try:
                        subprocess.run(command[1:], check=True)
                    except subprocess.CalledProcessError as e:
                        raise Exception(f"Failed to run command: {e.cmd}")

    def create(self, name, type, version):
        self.name = self.validate_name(name)
        self.type = self.validate_type(type)
        self.version = self.validate_version(version)
        self.path = os.path.join(self.path, self.name)
        os.mkdir(self.path)

        for file_name in self.REQUIRED_FILES:
            template_name = file_name
            if file_name == self.COMPONENT_FILE:
                template_name = f"{type}.py"
            template: Template = get_template(template_name)
            file = template.render(
                component_type=self.type,
                component_name=self.name,
                version=self.version
            )
            file_path = os.path.join(self.path, file_name)
            with open(file_path, "w+") as f:
                f.write(file)

    def push(self, type, token):
        self._load_component(type)
        file = self._get_component_zip()
        headers = {
            'Authorization': token
        }
        data = {
            'name': self.name,
            'version': self.version,
            'parameters': json.dumps(self.parameters),
        }
        # TODO: Support io, network
        if type == "algorithm":
            response = requests.post(f"{API_URL}/algorithm/", files=file, data=data, headers=headers)
            if response.status_code != 201:
                raise Exception(f"Failed to push component: {response.text}")
        else:
            raise NotImplementedError(f"Component type: {type} is not supported")
        return

    def pull(self, name, type, version, token):
        self.name = self.validate_name(name)
        self.type = self.validate_type(type)
        self.version = self.validate_version(version)
        headers = {
            'Authorization': token
        }
        data = {
            'type': self.type,
            'name': self.name,
            'version': version,
        }
        response = requests.post(f"{API_URL}/hub/pull/", data=data, headers=headers)

        if response.status_code != 200:
            if response.status_code == 404:
                raise Exception(f"Component not found")
            raise Exception(f"Failed to pull the component from splight hub")
            
        versioned_component_name = f"{self.name}-{self.version}"
        zip_filename = f"{versioned_component_name}.zip"
        try:
            with open(zip_filename, "wb") as f:
                f.write(response.content)

            component_path = os.path.join(self.path, versioned_component_name)
            with zipfile.ZipFile(zip_filename) as zip_ref:
                    os.mkdir(component_path)
                    zip_ref.extractall(component_path)
        except:
            raise Exception(f"Failed to extract the component from splight hub to local machine. Make sure there's no directory called {versioned_component_name} in {self.path}")
        finally:
            os.remove(zip_filename)

    def run(self, type, instance_id, namespace, run_spec):
        self.initialize()
        self._load_component(type)
        component_class = getattr(self.component, "Main")
        component_class(
            instance_id=instance_id,
            namespace=namespace,
            run_spec=run_spec
        )