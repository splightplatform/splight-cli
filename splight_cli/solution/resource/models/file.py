from splight_lib.models import File as FileSchema
from splight_lib.models.base import SplightDatabaseBaseModel

from splight_cli.solution.resource.models.base import Resource


class File(Resource):
    _schema: SplightDatabaseBaseModel = FileSchema
