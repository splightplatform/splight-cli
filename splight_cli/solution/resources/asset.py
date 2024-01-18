from splight_lib.models import Asset
from splight_lib.models.base import SplightDatabaseBaseModel

from splight_cli.solution.resources.base import Resource


class AssetResource(Resource):
    _schema: SplightDatabaseBaseModel = Asset
