from splight_lib.models import Component as ComponentSchema
from splight_lib.models.base import SplightDatabaseBaseModel

from splight_cli.solution.resource.models.base import Resource


class Component(Resource):
    _schema: SplightDatabaseBaseModel = ComponentSchema
