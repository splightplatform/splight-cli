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

    @property
    def _are_changes(self):
        return len(self._to_create + self._to_update + self._to_delete) != 0

    def sync(self, save=False):
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
        diffs = []
        for spec_resource in self._spec_resources:
            if not self._state.contains(
                spec_resource.name,
                spec_resource.type,
            ):
                self._to_create.append(spec_resource)
            else:
                data = self._state.get(spec_resource.name, spec_resource.type)
                state_resource = type_map[spec_resource.type](data)

                diff = state_resource.diff(spec_resource)
                if diff:
                    diffs.append(diff)
                    self._to_update.append(spec_resource)

        for _, type, data in self._state.all():
            state_resource = type_map[type](data)
            if state_resource not in self._spec_resources:
                self._to_delete.append(state_resource)

        if not self._are_changes:
            self._logger.no_changes()
        else:
            self._logger.plan()

    def apply(self):
        if not self._are_changes:
            return

        if not self._logger.apply():
            return

        for spec_resource in self._to_create:
            self._logger.resource_info("Creating resource...", spec_resource)
            spec_resource.create()

            self._state.add(
                spec_resource.name,
                spec_resource.type,
                spec_resource.dump(),
            )
            self._state.save()

        for spec_resource in self._to_update:
            data = self._state.get(spec_resource.name, spec_resource.type)
            state_resource = type_map[spec_resource.type](data)

            self._logger.resource_info("Updating resource...", spec_resource)
            state_resource.update(spec_resource)

            self._state.update(
                state_resource.name,
                state_resource.type,
                state_resource.dump(),
            )
            self._state.save()

        for state_resource in self._to_delete:
            self._logger.resource_info("Deleting resource...", state_resource)
            state_resource.delete()

            self._state.delete(state_resource.name, state_resource.type)
            self._state.save()
