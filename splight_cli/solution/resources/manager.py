from typing import List

from splight_cli.solution.resources.asset import AssetResource
from splight_cli.solution.resources.base import Resource
from splight_cli.solution.resources.file import FileResource
from splight_cli.solution.resources.logger import ResourceLogger
from splight_cli.solution.state import State

type_map = {
    "FileResource": FileResource,
    "AssetResource": AssetResource,
}


class ResourceManager:
    def __init__(self, spec_resources: List[Resource], state: State) -> None:
        self._state = state
        self._spec_resources = spec_resources
        self._to_create = []
        self._to_update = []
        self._to_delete = []

        self._logger = ResourceLogger()

    def sync(self, save=False):
        # Sync state resources with respect to the engine
        for _, type, data in self._state.all():
            state_resource = type_map[type](data)
            self._logger.resource_info("Refreshing state...", state_resource)
            state_resource.sync()
            self._state.update(
                state_resource.name,
                state_resource.type,
                state_resource.dump(),
            )
            if save:
                self._state.save()

    def plan(self):
        # TODO: append diffs to a list and print them?
        for spec_resource in self._spec_resources:
            if not self._state.contains(
                spec_resource.name,
                spec_resource.type,
            ):
                self._to_create.append(spec_resource)
            else:
                self._to_update.append(spec_resource)

        for _, type, data in self._state.all():
            state_resource = type_map[type](data)
            if state_resource not in self._spec_resources:
                self._to_delete.append(state_resource)

        if not self._to_create + self._to_update + self._to_delete:
            self._logger.event(
                "No changes. Your infrastructure matches the configuration.",
                bold=True,
                previous_line=True,
                new_line=True,
            )
            self._logger.event(
                "Splight has compared your real infrastructure against your configuration and found no differences, so no changes are needed.",
                new_line=True,
            )
        else:
            self._logger.event(
                "Splight solution will perform the following actions:",
                previous_line=True,
                new_line=True,
            )
            self._logger.event(
                f"Plan: {len(self._to_create)} to add, {len(self._to_update)} to change, {len(self._to_delete)} to destroy."
            )

    def apply(self):
        # TODO:
        # Do you want to perform these actions?
        # Terraform will perform the actions described above.
        # Only 'yes' will be accepted to approve.
        #
        # Enter a value:

        for spec_resource in self._to_create:
            # Create resource
            self._logger.resource_info("Creating resource...", spec_resource)
            spec_resource.create()

            # Save it to the state
            self._state.add(
                spec_resource.name,
                spec_resource.type,
                spec_resource.dump(),
            )
            self._state.save()

        for spec_resource in self._to_update:
            # Load resource from the state
            data = self._state.get(spec_resource.name, spec_resource.type)
            state_resource = type_map[spec_resource.type](data)

            # Update its parameters with the ones in spec
            self._logger.resource_info("Updating resource...", spec_resource)
            state_resource.update(spec_resource)

            # Update the state data for the resource
            self._state.update(
                state_resource.name,
                state_resource.type,
                state_resource.dump(),
            )
            self._state.save()

        for state_resource in self._to_delete():
            # Delete resource from the engine
            self._logger.resource_info("Deleting resource...", state_resource)
            state_resource.delete()

            # Delete resource from the state
            self._state.delete(state_resource.name, state_resource.type)
            self._state.save()
