import json
import os
from typing import Dict, Iterator
from urllib.parse import urlparse

import boto3
from pydantic import BaseModel, PrivateAttr, field_validator, model_validator
from splight_lib.models.component import abstractmethod
from splight_lib.settings import BaseSettings

from splight_cli.settings import AWSSettings
from splight_cli.solution.utils import bprint

# TODO: Make I/O asyncio safe


class UnexistingResourceException(Exception):
    def __init__(self, name):
        super().__init__(f"Resource with name '{name}' not found.")


class ResourceAlreadyExistsError(Exception):
    def __init__(self, name):
        super().__init__(f"Resource with name '{name}' already exists.")


class FileHandler(BaseModel):
    @abstractmethod
    def load(self) -> Dict:
        raise NotImplementedError()

    @abstractmethod
    def save(self) -> None:
        raise NotImplementedError()


class LocalFileHandler(FileHandler):
    path: str

    @field_validator("path", mode="after")
    def default_state_file(cls, value: str):
        if not value:
            value = "state.json"
            if not os.path.isfile(value):
                bprint(f"Creating state file at: '{value}'.")
                cls._dump_json({}, value)
            else:
                bprint(f"Using state file at: '{value}'.")
        return value

    def load(self) -> Dict:
        with open(self.path, "r") as fp:
            return json.load(fp)

    def save(self, state_data: Dict) -> None:
        self._dump_json(state_data, self.path)

    @staticmethod
    def _dump_json(data: Dict, file_path: str) -> None:
        with open(file_path, "w") as fp:
            json.dump(data, fp, indent=2)


class S3FileHandler(FileHandler):
    bucket: str
    key: str

    _settings: BaseSettings = PrivateAttr()
    _client = PrivateAttr()

    @model_validator(mode="after")
    def default_state_file(self):
        if not self.bucket:
            raise ValueError("Bucket can not be empty.")

        if not self.key:
            self.key = "state.json"
            # TODO: if file does not exist in S3
            if ...:
                bprint(f"Creating state file at: '{self.key}'.")
                self.save({})
            else:
                bprint(f"Using state file at: '{self.key}'.")

    @property
    def _settings(self):
        return AWSSettings()

    @property
    def _client(self):
        client = boto3.client(
            "s3",
            region_name=self._settings.DEFAULT_REGION,
            aws_access_key_id=self._settings.ACCESS_KEY_ID,
            aws_secret_access_key=self._settings.SECRET_ACCESS_KEY,
        )
        return client

    def load(self) -> Dict:
        response = self._client.get_object(Bucket=self.bucket, Key=self.key)
        state_data = json.loads(response["Body"].read().decode("utf-8"))
        return state_data

    def save(self, state_data: Dict) -> None:
        self._client.put_object(
            Bucket=self.bucket,
            Key=self.key,
            Body=json.dumps(state_data),
            ContentType="application/json",
        )


class StateData(BaseModel):
    resource_map: Dict = {}

    def _validate_name(self, name: str) -> None:
        if not isinstance(name, str):
            raise ValueError("Key must be a string.")

    def _validate_data(self, data: Dict) -> None:
        if not isinstance(data, Dict):
            raise ValueError("Data must be a dictionary.")

    def contains(self, name: str) -> bool:
        self._validate_name(name)
        return name in self.resource_map

    def get(self, name: str) -> Dict:
        self._validate_name(name)

        if name not in self.resource_map:
            raise UnexistingResourceException(name)

        return self.resource_map[name]

    def all(self) -> Iterator:
        return self.resource_map.items()

    # We must do the lookup by name, since IDs are never
    # present in the state representation
    # TODO: mantener las exceptions en los metodos CRUD para ids existentes y eso...
    def add(self, name: str, data: Dict) -> None:
        # TODO: save by res type si o si RESOLVER PRIMERO

        self._validate_name(name)
        self._validate_data(data)

        if name in self.resource_map:
            raise ResourceAlreadyExistsError(name)

        self.resource_map[name] = data

    # TODO: match this func names with the baseresource class
    def delete(self, name: str) -> None:
        self._validate_name(name)

        if name not in self.resource_map:
            raise UnexistingResourceException(name)

        del self.resource_map[name]

    def update(self, name: str, data: Dict) -> None:
        self._validate_name(name)
        self._validate_data(data)

        if name not in self.resource_map:
            raise UnexistingResourceException(name)

        self.resource_map[name] = data


class State(StateData):
    _file_handler: FileHandler = PrivateAttr()

    def __init__(self, uri: str = "") -> None:
        if not isinstance(uri, str):
            raise ValueError("State URI must be a string.")

        url = urlparse(uri)

        if url.scheme == "s3":
            file_handler = S3FileHandler(bucket=url.netloc, key=url.path)
        else:
            file_handler = LocalFileHandler(path=url.path)

        super().__init__(**file_handler.load())

        self._file_handler = file_handler

    def save(self) -> None:
        self._file_handler.save(self.model_dump())
