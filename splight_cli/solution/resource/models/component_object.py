from splight_lib.models import ComponentObject as ComponentObjectSchema
from splight_lib.models.base import SplightDatabaseBaseModel

from splight_cli.solution.resource.models.base import Resource


class ComponentObject(Resource):
    _schema: SplightDatabaseBaseModel = ComponentObjectSchema
