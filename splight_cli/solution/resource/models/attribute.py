from splight_lib.models import Attribute as AttributeSchema
from splight_lib.models.base import SplightDatabaseBaseModel

from splight_cli.solution.resource.models.base import Resource


class Attribute(Resource):
    _schema: SplightDatabaseBaseModel = AttributeSchema
