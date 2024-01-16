from splight_cli.solution.resources.asset import AssetResource
from splight_cli.solution.resources.file import FileResource

resource_map = {
    "FileResource": FileResource,
    "AssetResource": AssetResource,
    "files": FileResource,
    "assets": AssetResource,
}
