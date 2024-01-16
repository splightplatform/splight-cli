from typing import List

from splight_cli.solution.resources.base import Resource
from splight_cli.solution.resources.utils import resource_map
from splight_cli.solution.state import State

# TODO: Si esta en el state, tiene que tener ID
# TODO: Crear las cosas en orden de dependencia. Quizas usar dependencias como en DB
# TODO: Lo mismo para borrar. Deberias impedir borrar algo que dependa de otra cosa?
# TODO:


class ResourceManager:
    def __init__(
        self,
        spec_resources: List[Resource] = [],
        state: State = None,
    ) -> None:
        # Sync state resources with respect to the engine
        state_resources = []
        for name, data in state.all():
            resource = resource_map[data["type"]](**data["data"])
            resource.sync()
            state.update(name, resource.dump())

        __import__("ipdb").set_trace()
        for resource in spec_resources:
            if resource not in state_resources:
                pass
