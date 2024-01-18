import json
from typing import Dict, Iterator, Tuple

from pydantic import BaseModel


class UnexistingResourceException(Exception):
    def __init__(self, name):
        super().__init__(f"Resource with name '{name}' not found.")


class ResourceAlreadyExistsError(Exception):
    def __init__(self, name):
        super().__init__(f"Resource with name '{name}' already exists.")


class State(BaseModel):
    resources: Dict[str, Dict[str, Dict]] = {}

    def contains(self, name: str, type: str) -> bool:
        return type in self.resources and name in self.resources[type]

    def get(self, name: str, type: str) -> Dict:
        if not self.contains(name, type):
            raise UnexistingResourceException(name)
        return self.resources[type][name]

    def all(self) -> Iterator:
        for type, resources_of_type in self.resources.items():
            for name, data in resources_of_type.items():
                yield name, type, data

    def add(self, name: str, type: str, data: Dict) -> None:
        if type not in self.resources:
            self.resources[type] = {}
        if self.contains(name, type):
            raise ResourceAlreadyExistsError(name)
        self.resources[type][name] = data

    def delete(self, name: str, type: str) -> None:
        if not self.contains(name, type):
            raise UnexistingResourceException(name)
        del self.resources[type][name]
        if not self.resources[type]:
            del self.resources[type]

    def update(self, name: str, type: str, data: Dict) -> None:
        if not self.contains(name, type):
            raise UnexistingResourceException(name)
        self.delete(name, type)
        self.add(name, type, data)

    def load(self, path: str) -> None:
        with open(path, "r") as fp:
            self.resources = json.load(fp)

    def save(self, path: str) -> None:
        with open(path, "w") as fp:
            json.dump(self.resources, fp, indent=2)
