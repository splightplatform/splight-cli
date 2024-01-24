from splight_lib.models import Function as FunctionSchema
from splight_lib.models.base import SplightDatabaseBaseModel

from splight_cli.solution.resource.models.base import Resource


class Function(Resource):
    _schema: SplightDatabaseBaseModel = FunctionSchema
