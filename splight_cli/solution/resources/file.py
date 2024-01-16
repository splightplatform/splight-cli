from typing import Type

from splight_lib.models import File

from splight_cli.solution.resources.base import Resource


class FileResource(Resource):
    file: str

    @property
    def _schema(self):
        return File

    def __eq__(self, resource: Type["FileResource"]) -> bool:
        # TODO: omitir el ID
        if not isinstance(resource, File):
            return False
        return (
            self.name == resource.name
            and self._model.checksum == resource._model.checksum
        )
