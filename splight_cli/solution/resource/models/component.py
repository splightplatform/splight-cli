from splight_lib.models import Component as ComponentSchema
from splight_lib.models.base import SplightDatabaseBaseModel

from splight_cli.solution.resource.models.base import Resource


# FIXME: Compare with its hub component definition
# FIXME: Consider the component upgrade use case:
# - Use the CLI command maybe and then update the plan?
# - I think the validations against HUB are a prequisite.
class Component(Resource):
    _schema: SplightDatabaseBaseModel = ComponentSchema
