from typing import Any, Dict, List, Tuple

from splight_lib.models.base import SplightDatabaseBaseModel


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
        # TODO: must replace references before calling this
        self._schema(**self.arguments).save()

    def update(self) -> None:
        # TODO: arguments must be updated with spec before calling this
        self._schema(**self.arguments).save()

    def delete(self) -> None:
        # TODO: args must have an ID before calling this
        self._schema(**self.arguments).delete()

    def refresh(self) -> None:
        self.arguments = self._schema.retrieve(
            resource_id=self.id
        ).model_dump()

    def diff(self) -> None:
        pass

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
