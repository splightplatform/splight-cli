from typing import Dict, List

from toposort import toposort_flatten as toposort
from typer import confirm

from splight_cli.solution.resource.diff import Diff
from splight_cli.solution.resource.logger import ResourceLogger
from splight_cli.solution.resource.models import (
    Asset,
    Attribute,
    File,
    Function,
    Metadata,
    Resource,
    Secret,
)
from splight_cli.solution.state import State

type_map = {
    "Asset": Asset,
    "Attribute": Attribute,
    "Metadata": Metadata,
    "File": File,
    "Function": Function,
    "Secret": Secret,
}


# NOTE: One good thing about this approach, is that the code is idempotent.
# That means, if it fails, you can just fix your spec issues (inspect the traceback)
# and try again. The state won't loose its consistency.
# FIXME: Paralelize the processing of non dependent resources.
# Use toposort instead of toposort_flatten for this purpose.
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
            reference_target = reference["target"]
            reference_string = reference["string"]

            value = resource_pool[reference_key].id
            if value is None:
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
        # I would not alter the flow of this function since it covers up
        # all the possible edits you make to the spec file.

        plan = {}
        resources = {}

        # FIXME: dependency_graph order in delete
        # First remove the state items not present in the spec file
        for key in self._state.all():
            if key not in self._specs:
                data = self._state.get(key)

                resource = self._create_resource(data)

                diff = Diff(new_arguments={}, old_arguments=resource.arguments)
                plan[key] = {"operation": "deleted", "diff": diff}

        # Iterate over the resource specs in the spec file
        for key in self._specs_order:
            # If this resource does not exist yet
            if not self._state.contains(key):
                data = self._specs[key]

                resource = self._create_resource(data)
                resources[key] = resource

                # Replace each reference of this resource.
                # If it does not exist, we set the reference text
                # just to show in the plan what value will receive later.
                self._update_references(resource, resources)

                # We do not have previous arguments because this a new
                # resource.
                diff = Diff(new_arguments=resource.arguments, old_arguments={})
                plan[key] = {"operation": "created", "diff": diff}

            # Already exists in the engine
            else:
                state_data = self._state.get(key)
                state_resource = self._create_resource(state_data)

                spec_data = self._specs[key]
                spec_resource = self._create_resource(spec_data)

                # Replace each reference of this resource
                # Same thing as before.
                self._update_references(spec_resource, resources)

                diff = Diff(
                    new_arguments=spec_resource.arguments,
                    old_arguments=state_resource.arguments,
                )

                resources[key] = state_resource

                # This resource changed if the diff contains at least a line.
                # We ignore this resource if the arguments stay the same.
                # Note that we are comparing both arguments with their references
                # replaced.
                if diff:
                    plan[key] = {"operation": "updated", "diff": diff}

        if not plan:
            self._logger.event(
                "Your infrastructure matches the configuration."
            )
        else:
            # Just print some messages and the diff for each resource
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
        # I would not alter the flow of this function since it covers up
        # all the possible edits you make to the spec file.

        resources = {}

        self._logger.event(
            "Do you want to apply this changes?", bold=True, previous_line=True
        )
        if not confirm("Insert choice: "):
            self._logger.event("No actions performed")
            return

        # FIXME: dependency_graph order in delete
        # First remove the state items not present in the spec file
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
                state_data = self._state.get(key)
                state_resource = self._create_resource(state_data)

                spec_data = self._specs[key]
                spec_resource = self._create_resource(spec_data)

                # Replace each reference of this resource
                self._update_references(spec_resource, resources)

                diff = Diff(
                    new_arguments=spec_resource.arguments,
                    old_arguments=state_resource.arguments,
                )

                resources[key] = state_resource

                if diff:
                    state_resource.update_arguments(spec_resource.arguments)
                    state_resource.update()
                    self._logger.resource("Resource updated", state_resource)

                    self._state.update(key, state_resource.dump())
                    self._state.save()
