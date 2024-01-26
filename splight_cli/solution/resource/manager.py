from typing import Dict, List

from toposort import toposort_flatten as toposort

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

    def _create_resource(self, data):
        name = data["name"]
        type = data["type"]
        arguments = data["arguments"]
        depends_on = data["depends_on"]
        references = data["references"]

        resource = type_map[type](
            name=name,
            arguments=arguments,
            depends_on=depends_on,
            references=references,
        )
        return resource

    def _update_references(
        self, references: List[Dict], resources: List[Resource]
    ):
        # Replace each reference of this resource
        for reference in references:
            reference_key = reference["key"]
            reference_source = reference["source"]
            reference_target = reference["target"]
            reference_string = reference["string"]

            try:
                value = resources[reference_key].get_argument_value(
                    reference_source
                )
            except:
                value = reference_string

                # Replace it in our arguments.
                # TODO: falta el resource de origen
                resource.set_argument_value(reference_target, value)

    def refresh(self):
        for key in self._state.all():
            data = self._state.get(key)
            resource = self._create_resource(data)

            self._logger.resource("Refreshing state...", resource)
            resource.sync()

            self._state.update(
                resource.key,
                resource.dump(),
            )
            self._state.save()

    def plan(self):
        # TODO: Append orphans at the beggining
        # TODO: Delete them from the state (do not save it).

        to_create = 0
        to_update = 0
        to_delete = 0

        plan = []

        resources = {}

        for key in self._specs_order:
            # If this resource does not exist yet
            if key not in self._state:
                data = self._specs[key]

                resource = self._create_resource(data)
                resources[key] = resource

                # Replace each reference of this resource
                for reference in resource.references:
                    reference_key = reference["key"]
                    reference_source = reference["source"]
                    reference_target = reference["target"]
                    reference_string = reference["string"]

                    try:
                        value = resources[reference_key].get_argument_value(
                            reference_source
                        )
                    except:
                        value = reference_string

                    # Replace it in our arguments.
                    resource.set_argument_value(reference_target, value)

                diff = resource.diff({})
                plan.append(diff)

                to_create += 1

            # Already exists in the engine
            else:
                data = self._state.get(key)

                resource = self._create_resource(data)
                resources[key] = resource

                # Replace each reference of this resource
                for reference in resource.references:
                    reference_key = reference["key"]
                    reference_source = reference["source"]
                    reference_target = reference["target"]
                    reference_string = reference["string"]

                    try:
                        value = resources[reference_key].get_argument_value(
                            reference_source
                        )
                    except:
                        value = reference_string

                    # Replace it in our arguments.
                    resource.set_argument_value(reference_target, value)

                new_arguments = self._specs[key]["arguments"]

                diff = resource.diff(new_arguments)
                if diff:
                    plan.append(diff)
                    to_update += 1

        __import__("ipdb").set_trace()

    def apply(self):
        for resource in self._to_delete():
            resource.delete()
            self._state.delete(resource.key)
            self._state.save()

        for resource in self._to_create():
            # TODO: there might be pending references. We should always find them in this step
            resource.create()
            self._state.add(resource.key, resource.dump())
            self._state.save()

        for resource in self._to_update():
            # TODO: there might be pending references. We should always find them in this step
            resource.update_arguments(
                new_arguments
            )  # TODO: no olvidarte de esto en el apply
            resource.update()
            self._state.add(resource.key, resource.dump())
            self._state.save()
