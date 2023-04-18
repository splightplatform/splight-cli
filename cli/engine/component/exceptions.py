
class BadComponentId(Exception):
    """Exception raised when a component id is invalid."""
    def __init__(self, id: str):
            self._msg = (
                  f"Component with id {id} does not exist."
            )
    def __str__(self) -> str:
        return self._msg


class BadHubVersion(Exception):
    """Exception raised when a version is invalid."""
    def __init__(self, name: str, version: str):
            self._msg = (
                  f"Hub component {name} version {version} was not found."
            )
    def __str__(self) -> str:
        return self._msg

class VersionUpdated(Exception):
     """Exception raised when the component is updated."""
     def __init__(self, name: str, version: str):
             self._msg = (
                   f"Component {name} is already at version {version}."
             )
     def __str__(self) -> str:
         return self._msg