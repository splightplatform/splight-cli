class InvalidComponentId(Exception):
    """Exception raised when a component id is invalid."""
    def __init__(self, id: str):
            self._msg = (
                  f"Component with id {id} does not exist."
            )
    def __str__(self) -> str:
        return self._msg


class VersionUpdateError(Exception):
     """Exception raised when the component is updated."""
     def __init__(self, name: str, version: str):
             self._msg = (
                   f"Component {name} is already at version {version}."
             )
     def __str__(self) -> str:
         return self._msg