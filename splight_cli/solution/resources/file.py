from splight_lib.models import File
from splight_lib.models.base import SplightDatabaseBaseModel

from splight_cli.solution.resources.base import Resource


class FileResource(Resource):
    _schema: SplightDatabaseBaseModel = File

    def create(self) -> None:
        self._client.save()
