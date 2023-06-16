from typing import Dict


class InvalidComponentId(Exception):
    """Exception raised when a component id is invalid."""

    def __init__(self, id: str):
        self._msg = f"Component with id {id} does not exist."

    def __str__(self) -> str:
        return self._msg


class VersionUpdateError(Exception):
    """Exception raised when the component is already updated."""

    def __init__(self, name: str, version: str):
        self._msg = f"Component {name} is already at version {version}."

    def __str__(self) -> str:
        return self._msg


class ComponentCreateError(Exception):
    """Exception raised when the component could not be saved."""

    def __init__(
        self, name: str, version: str, input_params: Dict, msg: str = None
    ):
        self._msg = (
            f"An error occurred creating component {name}-{version}. "
            f"Input parameters: {input_params}."
            f"Error message: {msg}"
        )

    def __str__(self) -> str:
        return self._msg


class UpdateParametersError(Exception):
    """Exception when some parameter could not be updated."""

    def __init__(self, param: Dict):
        self._error = f"An error occurred updating parameter {param}"

    def __str__(self) -> str:
        return self._error
