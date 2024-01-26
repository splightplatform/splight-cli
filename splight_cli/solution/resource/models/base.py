from json import load
from typing import Any, Dict, List

from deepdiff import DeepDiff
from splight_lib.models.base import SplightDatabaseBaseModel


# TODO: clean not used properties and methods
class Resource:
    _schema: SplightDatabaseBaseModel = None

    def __init__(
        self,
        name: str,
        arguments: Dict = {},
        depends_on: List[str] = [],
        references: List[Dict] = [],
    ) -> None:
        if self._schema is None:
            raise NotImplementedError("Resources must define a schema.")

        self.name = name
        self.arguments = arguments
        self.depends_on = depends_on
        self.references = references

    @property
    def type(self) -> str:
        return self.__class__.__name__

    @property
    def key(self) -> str:
        return f"{self.type}:{self.name}"

    @property
    def id(self) -> str:
        return self._client.id

    def create(self) -> None:
        self._schema(**self.arguments).save()

    def update(self) -> None:
        self._schema(**self.arguments).save()

    def delete(self) -> None:
        self._schema(**self.arguments).delete()

    def refresh(self) -> None:
        # TODO: guardar el Id en el dump mepa...
        self.arguments = self._schema.retrieve(
            resource_id=self.id
        ).model_dump()

    def update_arguments(self, new_arguments: Dict) -> None:
        # TODO: update only the keys in the new arguments
        raise NotImplementedError()

    def diff(self, new_arguments: Dict) -> Dict:
        diff = DeepDiff(new_arguments, self.arguments)
        # TODO: solo chequear los que estan en los new args
        return diff

    def dump(self) -> Dict:
        return {
            "name": self.name,
            "type": self.type,
            "arguments": self.arguments,
            "depends_on": self.depends_on,
            "references": self.references,
        }

    def set_argument_value(self, path: List[str], value: Any):
        # Assumes the path exists
        current = self.arguments
        for key in path[:-1]:
            current = current[key]

        last_key = path[-1]

        if isinstance(current, dict):
            current[last_key] = value
        elif isinstance(current, list):
            current[int(last_key)] = value
        else:
            raise ValueError(f"Invalid path: {path}")

    def get_argument_value(self, path: List[str]) -> Any:
        # Assumes the path exists
        current = self.arguments
        for key in path:
            if isinstance(current, dict):
                current = current[key]
            elif isinstance(current, list):
                current = current[int(key)]
            else:
                raise ValueError(f"Invalid path: {path}")
            return current
