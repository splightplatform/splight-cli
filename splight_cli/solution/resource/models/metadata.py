from splight_lib.models import Metadata as MetadataSchema
from splight_lib.models.base import SplightDatabaseBaseModel

from splight_cli.solution.resource.models.base import Resource


class Metadata(Resource):
    _schema: SplightDatabaseBaseModel = MetadataSchema
