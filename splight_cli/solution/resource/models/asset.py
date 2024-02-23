from splight_lib.models import Asset as AssetSchema
from splight_lib.models.base import SplightDatabaseBaseModel

from splight_cli.solution.resource.models.base import Resource


class Asset(Resource):
    _schema: SplightDatabaseBaseModel = AssetSchema
