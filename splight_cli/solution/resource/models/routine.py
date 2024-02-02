from splight_lib.models import RoutineObject as RoutineSchema
from splight_lib.models.base import SplightDatabaseBaseModel

from splight_cli.solution.resource.models.base import Resource


# FIXME: compare with its component routine definition
class Routine(Resource):
    _schema: SplightDatabaseBaseModel = RoutineSchema
