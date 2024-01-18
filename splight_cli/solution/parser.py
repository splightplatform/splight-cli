import yaml

from splight_cli.solution.resources import AssetResource, FileResource

type_map = {
    "assets": AssetResource,
    "files": FileResource,
}


class Parser:
    def __init__(self, spec_file: str) -> None:
        try:
            with open(spec_file, "r") as fp:
                self._data = yaml.safe_load(fp)
        except FileNotFoundError:
            raise Exception(f"Spec file '{spec_file}' not found.")

    def load_resources(self):
        resources = []
        for resource_type in self._data:
            for resource_data in self._data[resource_type]:
                resources.append(
                    type_map[resource_type](
                        arguments=resource_data,
                    )
                )
        # TODO: this should load the dependencies for each resource
        return resources
