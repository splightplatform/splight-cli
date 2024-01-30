from typing import Dict, List

from toposort import toposort_flatten as toposort
from typer import confirm

from splight_cli.solution.resource.diff import Diff
from splight_cli.solution.resource.logger import ResourceLogger
from splight_cli.solution.resource.models import (
    Asset,
    File,
    Function,
    Resource,
)
from splight_cli.solution.state import State

type_map = {
    "Asset": Asset,
    "File": File,
    "Function": Function,
}


class ResourceManager:
    def __init__(
        self,
        state: State,
        specs: List[Resource] = [],
        dependency_graph: Dict = {},
    ) -> None:
        self._state = state
        self._specs = specs

        # Sort the resource specs by dependency order
        self._specs_order = toposort(dependency_graph)

        self._logger = ResourceLogger()

    def _create_resource(self, data: Dict):
        type = data.get("type")
        resource = type_map[type](**data)
        return resource

    def _update_references(
        self, resource: Resource, resource_pool: List[Resource]
    ):
        # Replace each reference of this resource
        for reference in resource.references:
            reference_key = reference["key"]
            reference_source = reference["source"]
            reference_target = reference["target"]
            reference_string = reference["string"]

            try:
                value = resource_pool[reference_key].get_argument_value(
                    reference_source
                )
            except:
                value = reference_string

                # Replace it in our arguments.
                resource.set_argument_value(reference_target, value)

    def refresh(self):
        for key in self._state.all():
            data = self._state.get(key)
            resource = self._create_resource(data)

            self._logger.resource("Refreshing state...", resource)
            resource.refresh()

            self._state.update(
                resource.key,
                resource.dump(),
            )
            self._state.save()

    def plan(self):
        plan = {}

        resources = {}

        for key in self._state.all():
            if key not in self._specs:
                data = self._state.get(key)

                resource = self._create_resource(data)

                diff = Diff(new_arguments={}, old_arguments=resource.arguments)
                plan[key] = {"operation": "deleted", "diff": diff}

        for key in self._specs_order:
            # If this resource does not exist yet
            if not self._state.contains(key):
                data = self._specs[key]

                resource = self._create_resource(data)
                resources[key] = resource

                # Replace each reference of this resource
                self._update_references(resource, resources)

                diff = Diff(new_arguments=resource.arguments, old_arguments={})
                plan[key] = {"operation": "created", "diff": diff}

            # Already exists in the engine
            else:
                data = self._state.get(key)

                resource = self._create_resource(data)
                resources[key] = resource

                # Replace each reference of this resource
                self._update_references(resource, resources)

                new_arguments = self._specs[key]["arguments"]

                diff = Diff(
                    new_arguments=new_arguments,
                    old_arguments=resource.arguments,
                )
                if diff:
                    plan[key] = {"operation": "updated", "diff": diff}

        if not plan:
            self._logger.event(
                "Your infrastructure matches the configuration."
            )
        else:
            self._logger.event(
                "Splight solution will perform the following actions:",
            )
            for key, data in plan.items():
                action = data["operation"]
                diff = data["diff"]

                type, name = key.split(":")
                self._logger.event(
                    f"Resource '{name}' of type '{type}' will be {action}:",
                    previous_line=True,
                )
                self._logger.diff(diff)

        return plan

    def apply(self):
        resources = {}

        self._logger.event(
            "Do you want to apply this changes?", bold=True, previous_line=True
        )
        if not confirm("Insert choice: "):
            self._logger.event("No actions performed")
            return

        for key in self._state.all():
            if key not in self._specs:
                data = self._state.get(key)

                resource = self._create_resource(data)

                resource.delete()
                self._logger.resource("Resource deleted", resource)

                self._state.delete(key)
                self._state.save()

        for key in self._specs_order:
            # If this resource does not exist yet
            if not self._state.contains(key):
                data = self._specs[key]

                resource = self._create_resource(data)
                resources[key] = resource

                # Replace each reference of this resource
                self._update_references(resource, resources)

                resource.create()
                self._logger.resource("Resource created", resource)

                self._state.add(resource.key, resource.dump())
                self._state.save()

            # Already exists in the engine
            else:
                data = self._state.get(key)

                resource = self._create_resource(data)
                resources[key] = resource

                # Replace each reference of this resource
                self._update_references(resource, resources)

                new_arguments = self._specs[key]["arguments"]

                diff = Diff(new_arguments, resource.arguments)
                if diff:
                    resource.update_arguments(new_arguments)
                    resource.update()
                    self._logger.resource("Resource updated", resource)

                    self._state.update(resource.key, resource.dump())
                    self._state.save()
