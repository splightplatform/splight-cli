class HubComponentNotFound(Exception):
    """Exception raised when a version is invalid."""

    def __init__(self, name: str, version: str):
        self._msg = f"Hub component {name} version {version} not found."

    def __str__(self) -> str:
        return self._msg
