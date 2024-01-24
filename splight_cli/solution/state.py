import json
from os.path import isfile
from typing import Dict, Iterator

from pydantic import BaseModel


class UnexistingResourceException(Exception):
    def __init__(self, key):
        super().__init__(f"Resource '{key}' not found.")


class ResourceAlreadyExistsError(Exception):
    def __init__(self, key):
        super().__init__(f"Resource '{key}' already exists.")


class State(BaseModel):
    resources: Dict = {}
    path: str

    def contains(self, key: str) -> bool:
        return key in self.resources

    def get(self, key: str) -> Dict:
        if not self.contains(key):
            raise UnexistingResourceException(key)
        return self.resources[key]

    def all(self) -> Iterator:
        return self.resources.keys()

    def add(self, key: str, id: str) -> None:
        if self.contains(key):
            raise ResourceAlreadyExistsError(key)
        self.resources[key] = id

    def delete(self, key: str) -> None:
        if not self.contains(key):
            raise UnexistingResourceException(key)
        del self.resources[key]

    def update(self, key: str, id: str) -> None:
        if not self.contains(key):
            raise UnexistingResourceException(key)
        self.delete(key)
        self.add(key, id)

    def load(self) -> None:
        if isfile(self.path):
            with open(self.path, "r") as fp:
                self.resources = json.load(fp)

    def save(self) -> None:
        with open(self.path, "w") as fp:
            json.dump(self.resources, fp, indent=2)
