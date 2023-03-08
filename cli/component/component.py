import os
import uuid
from typing import Dict, List, Optional

from jinja2 import Template
from splight_lib.execution import Thread
from rich.console import Console

from cli.component.loaders import ComponentLoader, InitLoader, SpecLoader
from cli.component.spec import Spec
from cli.component.exceptions import (
    InvalidSplightCLIVersion,
    ReadmeExists
)
from cli.constants import (
    COMPONENT_FILE,
    README_FILE_1
)
from cli.hub.component.hub_manager import HubComponentManager
from splight_models import HubComponent, Component as ComponentModel
from cli.utils import get_template
from cli.version import __version__

console = Console()

class Component:
    name = None
    version = None

    def __init__(self, context):
        self.context = context

    def create(self, name: str, version: str = "0.1.0", component_path: str = ""):
        Spec.verify(
            {
                "name": name,
                "version": version,
                "splight_cli_version": __version__,
                "custom_types": [],
                "input": [],
                "output": [],
                "endpoints": [],
            }
        )

        if not os.path.exists(component_path):
            component_path = os.path.join(f"{component_path}")
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
                splight_cli_version=__version__,
            )
            with open(file_path, "w+") as f:
                f.write(file)

    def run(
        self,
        path: str,
        input_parameters: Optional[List[Dict]] = None,
        component_id: str = None,
    ):
        # Load py module and validate Splight Component structure
        loader = ComponentLoader(path=path)
        component_class = loader.load()
        # Load json and validate Spec structure
        loader = SpecLoader(path=path)

        remote_input_parameters = []
        if component_id:
            db_client = self.context.framework.setup.DATABASE_CLIENT()
            components = db_client._get(resource_type=ComponentModel)

            component_input = components[0].input
            from_component = components[0]
            for component in components:
                if component.id == component_id:
                    component_input = component.input

            # print("HOLAAAA",component_input)

            for input in component_input:
                remote_input_parameters.append(input.__dict__)

        # HACER COMPONENT MANAGER
        # componentmanager.get(component_id)

        # /hub/mine -> engine/component/components : de ahi saco los input_parameters
        
        # 1. input_parameters
        # 2. component_id
        # 3. null

        run_spec = loader.load(
            input_parameters=remote_input_parameters,
            # manager=manager,
            component_id=component_id
        )
        self._validate_cli_version(run_spec.splight_cli_version)
        component = component_class(
            run_spec=run_spec.dict(),
            initial_setup=self.context.workspace.settings.dict(),
            component_id=component_id,
        )
        component.execution_client.start(Thread(target=component.start))

    def upgrade(self, from_component_id: str, to_component_id: str):
        db_client = self.context.framework.setup.DATABASE_CLIENT()
        components = db_client._get(resource_type=ComponentModel)

        to_component = components[0]
        from_component = components[0]
        for component in components:
            if component.id == from_component_id:
                from_component = component
            elif component.id == to_component_id:
                to_component = component

        old_input = from_component.input
        new_input = to_component.input
        for new in new_input:
            for old in old_input:
                if new.name == old.name:
                    new.value = old.value

        to_component.input = new_input

        # TODO: hay que pasar los objects!!!

        db_client._update(path="v2/engine/component/components", resource_id=to_component_id, data=to_component)

    def install_requirements(self, path: str):
        loader = InitLoader(path=path)
        loader.load()

    def _validate_cli_version(self, component_cli_version: str):
        if component_cli_version != __version__:
            raise InvalidSplightCLIVersion(component_cli_version, __version__)

    def readme(self, path: str, force: Optional[bool] = False):
        loader = SpecLoader(path=path)
        spec = loader.load().dict()
        name, version = spec["name"], spec["version"]
        if os.path.exists(os.path.join(path, README_FILE_1)):
            if not force:
                raise ReadmeExists(path)
            else:
                os.remove(os.path.join(path, README_FILE_1))
        template = get_template("auto_readme.md")
        readme = template.render(
            component_name=name,
            version=version,
            component_type=spec.get("component_type",""),
            inputs=spec.get("input", []),
            bindings=spec.get("bindings",[]),
            output=spec.get("output", []),
        )
        with open(os.path.join(path, README_FILE_1), "w+") as f:
            f.write(readme)
        console.print(f"{README_FILE_1} created for {name} {version}")
