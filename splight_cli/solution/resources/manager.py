from typing import List

from splight_cli.solution.resources.asset import AssetResource
from splight_cli.solution.resources.base import Resource
from splight_cli.solution.resources.file import FileResource
from splight_cli.solution.state import State

type_map = {
    "FileResource": FileResource,
    "AssetResource": AssetResource,
}


class ResourceManager:
    def sync(self, state: State):
        # Sync state resources with respect to the engine
        for _, type, data in state.all():
            state_resource = type_map[type](data)
            state_resource.sync()
            state.update(
                state_resource.name,
                state_resource.type,
                state_resource.dump(),
            )
            state.save()

    def create(self, spec_resources: List[Resource], state: State):
        # Create or update resources if they are present
        # in the state or not
        for spec_resource in spec_resources:
            if not state.contains(spec_resource.name, spec_resource.type):
                # Check for dependencies first
                # After dependencies create, extract their ID and replace
                # the placeholders.
                # ...

                # Create resource
                __import__("ipdb").set_trace()
                spec_resource.create()

                # Save it to the state
                state.add(
                    spec_resource.name,
                    spec_resource.type,
                    spec_resource.dump(),
                )
                state.save()
            else:
                data = state.get(spec_resource.name, spec_resource.type)
                state_resource = type_map[spec_resource.type](data)
                state_resource.update(spec_resource)
                state.update(
                    state_resource.name,
                    state_resource.type,
                    state_resource.dump(),
                )
                state.save()

    def delete(self, spec_resources: List[Resource], state: State):
        # Delete resources not defined by the spec file
        for state_resource in state.all():
            if state_resource not in spec_resources:
                state_resource.delete()
                state.delete(state_resource)
                state.save()
