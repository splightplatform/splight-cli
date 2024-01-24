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

    def apply(self):
        # TODO: Append orphans at the beggining
        # TODO: Delete them from the state too (dry run in plan).

        __import__("ipdb").set_trace()
        resources = {}
        for key in self._specs_order:
            data = self._specs[key]

            resource = self._create_resource(data)
            resources[key] = resource

            # Busco la referencia en los previous arguments del resource que referencio.
            for (
                reference
            ) in resource.references:  # TODO: better way to iterate this
                reference_key = reference["key"]
                reference_source = reference["source"]
                reference_target = reference["target"]

                # We should find it, since the referenced resource was already processed.
                # We can retrieve the value from the resources map or the state,
                # since both are in sync.
                value = resources[reference_key].get_argument_value(
                    reference_source
                )

                # Replace it in our arguments.
                resource.set_argument_value(reference_target, value)

            # HASTA ACA VENIAS MORTAL.
            # YO CREO QUE EL PROBLEMA RADICA EN QUE PREVIOUS ARGUMENTS ES LO QUE TIENE API.
            # ES IMPOSIBLE QUE EL DIFF RETORNE VACIO.

            # Tenes que hacer que el refresh del baseresource, actualize los args que ya tenias
            # pero solamente los IDs? esto siempre daría diff contra el spec

            # Solamente las keys de los arguments en el spec? <-- esto puede ser
            # Hay que resolver esta biyeccion con mati

            # spec_arguments <-> state_arguments <-> API

            # La cagada es que tampoco puedo simular, como podria cambiar el objeto en API
            # si lo crease con los arguments del spec

            # We have not created this resource
            if key not in self._state:
                diff = resource.diff({})
                resource.create()

                # TODO: do a refresh so you get the new arguments from API
                self._state.add(key, resource.dump())

            # This resource already exists
            else:
                state_data = self._state.get(key)
                diff = resource.diff(state_data["arguments"])
                if diff:
                    # TODO: Implementar bien este update
                    resource.update()

                    # TODO: do a refresh so you get the new arguments from API
                    self._state.update(key, resource.dump())

    def plan(self):
        # Si no existe esa key en el state:
        #     Dejas la referencia sin reemplazar
        # Else
        #     La reemplazo
        pass
