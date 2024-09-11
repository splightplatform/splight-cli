class ServerAlreadyExists(Exception):
    def __init__(self, name: str, version: str):
        self._msg = f"Server {name}-{version} already exists in HUB"

    def __str__(self) -> str:
        return self._msg


class ServerDirectoryAlreadyExists(Exception):
    def __init__(self, directory: str):
        self._msg = f"Directory with name {directory} already exists in path"

    def __str__(self) -> str:
        return self._msg


class HubServerNotFound(Exception):
    """Exception raised when a version is invalid."""

    def __init__(self, name: str, version: str):
        self._msg = f"Hub server {name} version {version} not found."

    def __str__(self) -> str:
        return self._msg


class BuildError(Exception):
    pass
