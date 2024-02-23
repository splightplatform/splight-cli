from typing import Any, Dict, List, Optional

from splight_lib.models.base import SplightDatabaseBaseModel

from splight_cli.solution.dict import get_dict_value, set_dict_value, walk_dict


class Resource:
    _schema: SplightDatabaseBaseModel = None

    def __init__(
        self,
        name: str,
        type: str,
        id: Optional[str] = None,
        arguments: Dict = {},
        depends_on: List[str] = [],
        references: List[Dict] = [],
    ) -> None:
        if self._schema is None:
            raise NotImplementedError("Resources must define a schema.")

        self.name = name
        self.type = type
        self.id = id
        self.arguments = arguments
        self.depends_on = depends_on
        self.references = references

    @property
    def key(self) -> str:
        return f"{self.type}:{self.name}"

    def create(self) -> None:
        client = self._schema(**self.arguments)
        client.save()
        self.id = client.id

    def update(self) -> None:
        self._schema(id=self.id, **self.arguments).save()

    def delete(self) -> None:
        self._schema(id=self.id, **self.arguments).delete()

    def refresh(self) -> None:
        # NOTE: override this method if you need to process an
        # incoming value (i.e decrypt secret before setting the argument
        # value)
        new_arguments = self._schema.retrieve(self.id).model_dump()
        for path, _ in walk_dict(self.arguments):
            try:
                new_value = get_dict_value(path, new_arguments)
            except:
                # This happens because the user gave a wrong extra attribute
                # and was ignored by API so it is not present in the new arguments.
                # By improving the function get_dict_value we could simplify
                # this code
                # Also this check is not necessary if we validate a JSON Schema
                # previously in the parser class.
                continue
            self.set_argument_value(path, new_value)

    def dump(self) -> Dict:
        return {
            "name": self.name,
            "id": self.id,
            "type": self.type,
            "arguments": self.arguments,
            "depends_on": self.depends_on,
            "references": self.references,
        }

    def update_arguments(self, new_arguments: Dict) -> None:
        self.arguments = new_arguments

    def set_argument_value(self, path: List[str], value: Any):
        return set_dict_value(value, path, self.arguments)
