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
