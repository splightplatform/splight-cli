from typing import Type

from splight_lib.models import Asset

from splight_cli.solution.resources.base import Resource


class AssetResource(Resource):
    name: str

    @property
    def _schema(self):
        return Asset

    def __eq__(self, resource: Type["AssetResource"]) -> bool:
        # TODO: aca omitir el id por ejemplo
        if not isinstance(resource, Asset):
            return False
        return self.name == resource.name
