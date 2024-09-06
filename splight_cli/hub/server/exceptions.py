from json import loads


class SpecFormatError(Exception):
    def __init__(self, error):
        self._msg = f"Error while parsing 'spec.json': {error}"

    def __str__(self) -> str:
        return self._msg


class SpecValidationError(Exception):
    def __init__(self, error):
        field = loads(error.json())[0]["loc"][0]
        message = loads(error.json())[0]["msg"]
        self._msg = (
            f"Validation error for field in 'spec.json': '{field}' {message}"
        )

    def __str__(self) -> str:
        return self._msg


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


class BuildError(Exception): ...
