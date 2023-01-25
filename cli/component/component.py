import os
import uuid
from typing import Dict, List, Optional

from jinja2 import Template
from splight_lib.execution import Thread

from cli.component.loaders import ComponentLoader, InitLoader, SpecLoader

from cli.component.spec import Spec
from cli.constants import COMPONENT_FILE
from cli.utils import get_template
from cli.version import __version__


class Component:
    name = None
    version = None

    def __init__(self, context):
        self.context = context

    def create(self, name, version):
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
        run_spec = loader.load(input_parameters=input_parameters)
        component = component_class(
            run_spec=run_spec.dict(),
            initial_setup=self.context.workspace.settings.dict(),
            component_id=component_id,
        )
        component.execution_client.start(Thread(target=component.start))

    def install_requirements(self, path: str):
        loader = InitLoader(path=path)
        loader.load()
