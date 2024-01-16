from abc import ABC, abstractmethod
from typing import Dict, Type

from pydantic import BaseModel, computed_field


class AbstractResource(ABC):
    @property
    @abstractmethod
    def _schema(self):
        pass

    @property
    @abstractmethod
    def _model(self):
        pass

    @property
    @abstractmethod
    def name(self):
        pass

    @abstractmethod
    def create(self, *args, **kwargs) -> None:
        pass

    @abstractmethod
    def update(self, resource: Type["AbstractResource"]) -> None:
        pass

    @abstractmethod
    def delete(self, *args, **kwargs) -> None:
        pass

    @abstractmethod
    def sync(self, id: str) -> None:
        pass

    @abstractmethod
    def dump(self) -> None:
        pass

    @abstractmethod
    def __eq__(self, __value: object) -> bool:
        pass


class Resource(AbstractResource, BaseModel):
    def __init__(self, **args) -> None:
        super().__init__(**args)
        self.__model = self._schema(**args)

    @property
    def _schema(self):
        raise NotImplementedError()

    @computed_field
    @property
    def type(self) -> str:
        return self.__class__.__name__

    @computed_field
    @property
    def model_data(self) -> Dict:
        return self.__model

    @property
    def _model(self) -> Dict:
        return self.__model

    @_model.setter
    def _model(self, value):
        self.__model = value

    @property
    def name(self):
        return self._model.name

    def create(self) -> None:
        self._model.save()

    def update(self, resource: Type["AbstractResource"]) -> None:
        if self.name != resource.name:
            raise ValueError(
                "Can not update resource using another one with a different name"
            )

        self._model.model_validate(resource.dump()).save()
        # TODO: ojo que no se updatean bien

    def delete(self) -> None:
        self._model.delete()
        # TODO: borrar ID? reinicializar?

    def sync(self) -> None:
        self._model = self._model.model_validate(
            self._model.retrieve(resource_id=self._model.id).model_dump()
        )

    def dump(self) -> None:
        return self.model_dump()
