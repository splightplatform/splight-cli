class ComponentAlreadyExists(Exception):
    def __init__(self, name: str, version: str):
        self._msg = f"Component {name}-{version} already exists in HUB"

    def __str__(self) -> str:
        return self._msg


class ComponentPullError(Exception):
    def __init__(self, name: str, version: str):
        self._msg = f"An error occurred pulling component {name}-{version}"

    def __str__(self) -> str:
        return self._msg


class ComponentPushError(Exception):
    def __init__(self, name: str, version: str):
        self._msg = f"An error occurred pushing component {name}-{version}"

    def __str__(self) -> str:
        return self._msg


class ComponentDirectoryAlreadyExists(Exception):
    def __init__(self, directory: str):
        self._msg = f"Directory with name {directory} already exists in path"

    def __str__(self) -> str:
        return self._msg


class HubComponentNotFound(Exception):
    """Exception raised when a version is invalid."""

    def __init__(self, name: str, version: str):
        self._msg = f"Hub component {name} version {version} not found."

    def __str__(self) -> str:
        return self._msg
