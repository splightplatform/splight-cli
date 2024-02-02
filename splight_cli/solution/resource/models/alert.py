from splight_lib.models import Alert as AlertSchema
from splight_lib.models.base import SplightDatabaseBaseModel

from splight_cli.solution.resource.models.base import Resource


class Alert(Resource):
    _schema: SplightDatabaseBaseModel = AlertSchema
