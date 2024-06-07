class HubSolutionAlreadyExists(Exception):
    def __init__(self, name: str, version: str):
        self._msg = f"Solution {name}-{version} already exists in Splight Hub"

    def __str__(self) -> str:
        return self._msg


class HubSolutionNotFound(Exception):
    def __init__(self, name: str, version: str):
        self._msg = f"Solution {name}-{version} not found in Splight Hub"

    def __str__(self) -> str:
        return self._msg


class MissingSolutionFile(Exception):
    def __init__(self, name: str, path: str):
        self._msg = f"Missing solution file {name} in path {path}"

    def __str__(self) -> str:
        return self._msg


class SolutionDirectoryAlreadyExists(Exception):
    def __init__(self, path: str):
        self._msg = f"Solution directory {path} already exists"

    def __str__(self) -> str:
        return self._msg
