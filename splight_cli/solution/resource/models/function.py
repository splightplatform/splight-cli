from splight_lib.models import Function as FunctionSchema
from splight_lib.models.base import SplightDatabaseBaseModel

from splight_cli.solution.resource.models.base import Resource


# FIXME: Sometimes the API mixes up the order of the function items after
# creating the resource, this causes the plan to show a diff.
# Another apply will fix it, but would be nice if we always sorted new
# and older arguments by name.
# Should be done by overriding init and after refresh retrieves the new
# arguments.
class Function(Resource):
    _schema: SplightDatabaseBaseModel = FunctionSchema
