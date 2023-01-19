import uuid
import os
from typing import List, Optional, Dict
from jinja2 import Template
from splight_lib.execution import Thread
from splight_lib import logging
from cli.version import __version__
from cli.constants import (
    COMPONENT_FILE,
)
from cli.utils import (
    get_template,
    validate_path_isdir,
)
from cli.component.handler import ComponentHandler
from cli.component.spec import Spec
from cli.component.loaders import SpecLoader, ComponentLoader
from cli.component.exceptions import ComponentAlreadyExistsException, ComponentDirectoryAlreadyExists


logger = logging.getLogger()


class Component:
    name = None
    version = None

    def __init__(self, context):
        self.context = context

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
            "splight_cli_version": __version__,
            "custom_types": [],
            "input": [],
            "output": [],
            "endpoints": [],
        })

        component_path = os.path.join(f"{name}", f"{version}")
        os.makedirs(component_path)

        for file_name in ComponentLoader.REQUIRED_FILES:
            template_name = file_name
            file_path = os.path.join(component_path, file_name)
            component_id = str(uuid.uuid4())
            if file_name == COMPONENT_FILE:
                template_name = "component.py"
            template: Template = get_template(template_name)
            file = template.render(
                component_name=name,
                version=version,
                component_id=component_id,
                splight_cli_version=__version__
            )
            with open(file_path, "w+") as f:
                f.write(file)

    def pull(self, name, version):
        versioned_name = f"{name}-{version}"
        component_path = os.path.join(versioned_name)

        if os.path.exists(component_path):
            raise ComponentDirectoryAlreadyExists(versioned_name)

        handler = ComponentHandler(self.context)
        handler.download_component(name, version)

    def delete(self, name, version):
        handler = ComponentHandler(self.context)
        handler.delete_component(name, version)

    def push(self, path: str, force = False):
        # Load py module and validate Splight Component structure 
        loader = ComponentLoader(path=path)
        _ = loader.load()
        # Load json and validate Spec structure 
        loader = SpecLoader(path=path)
        spec = loader.load()

        # TODO simplify this
        handler = ComponentHandler(self.context)
        if not force and handler.exists_in_hub(
            spec.name,
            spec.version
        ):
            raise ComponentAlreadyExistsException(f'{spec.name}-{spec.version}')
        handler.upload_component(
            privacy_policy=spec.privacy_policy,
            name=spec.name,
            version=spec.version,
            tags=spec.tags,
            custom_types=spec.custom_types,
            input=spec.input,
            output=spec.output,
            commands=spec.commands,
            bindings=spec.bindings,
            endpoints=spec.endpoints,
            splight_cli_version=spec.splight_cli_version,
            path=path,
        )

    def run(self, path: str, input_parameters: Optional[List[Dict]] = None):
        # Load py module and validate Splight Component structure 
        loader = ComponentLoader(path=path)
        component_class = loader.load()
        # Load json and validate Spec structure 
        loader = SpecLoader(path=path)
        run_spec = loader.load(input_parameters=input_parameters)
        component = component_class(
            run_spec=run_spec.dict(),
            initial_setup=self.context.workspace.settings.dict()
        )
        component.execution_client.start(Thread(target=component.start))

    def install_requirements(self, path: str):
        #IMPORTANT THIS SHOULD BE OK FOR BUILD
        raise NotImplementedError