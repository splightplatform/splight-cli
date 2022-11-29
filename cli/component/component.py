import subprocess
import importlib
import sys
import os
from typing import List, Type
from jinja2 import Template
from tempfile import NamedTemporaryFile
from cli.context import PrivacyPolicy

from splight_lib.component import AbstractComponent
from splight_lib.execution import Thread
from splight_lib import logging

from cli.constants import (
    COMPONENT_FILE,
    INIT_FILE,
    MAIN_CLASS_NAME,
    PICTURE_FILE,
    REQUIRED_FILES,
    SPEC_FILE,
    VARS_FILE,
)
from cli.utils import (
    api_get,
    get_template,
    validate_path_isdir,
)
from cli.component.handler import ComponentHandler, UserHandler
from cli.component.spec import Spec
from cli.component.loaders import SpecJSONLoader, SpecArgumentLoader

logger = logging.getLogger()


class ComponentAlreadyExistsException(Exception):
    pass


class Component:
    name = None
    version = None

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
            Spec.verify(self.spec)
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

    def _load_component(self) -> None:
        self.component = self._import_component()
        self._validate_component()

    def _load_component_in_push(self, no_import) -> None:
        if no_import:
            self.component = None
            Spec.verify(self.spec)
        else:
            self.component = self._import_component()
            self._validate_component()

    def _load_spec(self, raw_spec):
        self.spec = raw_spec
        self.name = self.spec["name"]
        self.tags = self.spec["tags"]
        self.version = self.spec["version"]
        self.custom_types = self.spec["custom_types"]
        self.input = self.spec["input"]
        self.output = self.spec["output"]
        self.commands = self.spec.get("commands", [])

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
        base_url = self.context.workspace.settings.SPLIGHT_PLATFORM_API_HOST
        file_data = api_get(
            f"{base_url}/hub/random_picture/",
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

    def _reset_input(self):
        for param in self.input:
            param_type = param["type"]
            if param_type in ["str", "int", "bool", "float"]:
                continue
            param["value"] = None

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
    def list(cls, context):
        handler = ComponentHandler(context)
        return handler.list_components()

    @classmethod
    def versions(cls, context, name):
        handler = ComponentHandler(context)
        return handler.list_component_versions(name)

    def create(self, name, version):
        Spec.verify({
            "name": name,
            "version": version,
            "custom_types": [],
            "input": [],
            "output": [],
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
                template_name = "component.py"
            template: Template = get_template(template_name)
            file = template.render(
                component_name=name, version=version
            )
            with open(file_path, "w+") as f:
                f.write(file)

    def push(self, force, public):
        self._validate_component_structure()
        loader = SpecJSONLoader(
            spec_file_path=self.spec_file,
            check_input=False
        )
        self.run_spec = loader.load_spec()
        self._load_spec(self.run_spec)
        self._reset_input()
        self._load_component()

        handler = ComponentHandler(self.context)
        if not force and handler.exists_in_hub(
            self.name, self.version
        ):
            raise ComponentAlreadyExistsException
        component = handler.get_component_info(
            self.name,
            self.version
        )
        current_policy = PrivacyPolicy.PRIVATE.value
        if component:
            current_policy = component["privacy_policy"]

        privacy_policy = PrivacyPolicy.PUBLIC.value if public else current_policy

        handler.upload_component(
            privacy_policy,
            self.name,
            self.version,
            self.tags,
            self.custom_types,
            self.input,
            self.output,
            self.commands,
            self.path
        )

    def pull(self, name, version):

        versioned_name = f"{name}-{version}"
        component_path = os.path.join(self.path, versioned_name)

        if os.path.exists(component_path):
            raise Exception(
                f"Directory with name {versioned_name} already exists in path"
            )

        handler = ComponentHandler(self.context)
        handler.download_component(name, version, self.path)

    def delete(self, name, version):
        handler = ComponentHandler(self.context)
        handler.delete_component(name, version)

    def run(self, run_spec: str):
        self._validate_component_structure()

        if run_spec:
            loader = SpecArgumentLoader(
                spec_json=run_spec
            )
        else:
            loader = SpecJSONLoader(
                spec_file_path=self.spec_file,
                check_input=True
            )
        self.run_spec = loader.load_spec()

        self._load_spec(self.run_spec)
        self._load_component()

        component_class = getattr(self.component, MAIN_CLASS_NAME)
        component = component_class(
            run_spec=self.run_spec,
            initial_setup=self.context.workspace.settings.dict()
        )
        component.execution_client.start(Thread(target=component.start))
