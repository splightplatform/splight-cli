from typing import Dict, Type

from deepdiff import DeepDiff
from splight_lib.models.base import SplightDatabaseBaseModel


class Resource:
    _schema: SplightDatabaseBaseModel = None

    def __init__(
        self,
        arguments: Dict = {},
    ) -> None:
        if self._schema is None:
            raise NotImplementedError("Resources must define a schema.")

        if arguments:
            self._client = self._schema(**arguments)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self.name == other.name

    def diff(self, spec_resource: Type["Resource"]):
        if not isinstance(spec_resource, self.__class__):
            return False

        # Only consider changes made to the spec resource
        # arguments
        diff = DeepDiff(
            spec_resource.dump(
                exclude_unset=True,
                exclude_none=True,
            ),
            self.dump(),
        )
        del diff["dictionary_item_added"]
        return diff

    @property
    def name(self) -> str:
        return self._client.name

    @property
    def type(self) -> str:
        return self.__class__.__name__

    @property
    def id(self) -> str:
        return self._client.id

    def create(self) -> None:
        self._client.save()

    def update(self, spec_resource: Type["Resource"]) -> None:
        self._client = self._client.model_copy(
            update=spec_resource.dump(
                exclude_unset=True,
                exclude_none=True,
            ),
        )
        self._client.save()

    def delete(self) -> None:
        self._client.delete()

    def sync(self) -> None:
        self._client = self._schema.retrieve(resource_id=self.id)

    def dump(
        self, exclude_unset: bool = False, exclude_none: bool = False
    ) -> Dict:
        return self._client.model_dump(
            exclude_unset=exclude_unset,
            exclude_none=exclude_none,
        )
