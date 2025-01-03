import json
import os

import pathspec
from pydantic import ValidationError
from rich.console import Console
from rich.table import Table
from splight_lib.models import HubComponent

from splight_cli.constants import SPEC_FILE, SPLIGHT_IGNORE, success_style
from splight_cli.hub.component.component_builder import ComponentBuilder
from splight_cli.hub.exceptions import SpecFormatError, SpecValidationError

console = Console()


class HubComponentManager:
    def build(self, path: str):
        try:
            with open(os.path.join(path, SPEC_FILE)) as fid:
                spec = json.load(fid)
        except Exception as exc:
            raise SpecFormatError(exc)

        # Validate spec fields before pushing the model
        try:
            component = HubComponent.model_validate(spec)
        except ValidationError as exc:
            raise SpecValidationError(exc)

        builder = ComponentBuilder(spec, path)
        builder.build()

        console.print(
            f"Component {component.id} build succesfully", style=success_style
        )

    def list_components(self):
        components = HubComponent.list(limit_=10000)
        names = set([component.name for component in components])
        table = Table("Name")
        [table.add_row(name) for name in names]
        console.print(table)

    def versions(self, name: str):
        components = HubComponent.list(name=name)
        table = Table("Name", "Version", "Verification", "Privacy Policy")
        for item in components:
            table.add_row(
                name, item.version, item.verification, item.privacy_policy
            )
        console.print(table)

    def _get_ignore_pathspec(self, path):
        try:
            with open(
                os.path.join(path, SPLIGHT_IGNORE), "r"
            ) as splightignore:
                return pathspec.PathSpec.from_lines(
                    "gitwildmatch", splightignore
                )
        except FileNotFoundError:
            return None
