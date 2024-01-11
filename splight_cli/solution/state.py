import json
from typing import Dict
from urllib.parse import urlparse

import boto3
from pydantic import BaseModel, PrivateAttr
from splight_lib.models.component import abstractmethod
from splight_lib.settings import BaseSettings

from splight_cli.settings import AWSSettings


# TODO: make this asyncio safe everywhere
# TODO: test bucket I/O
class UnexistingResourceException(Exception):
    def __init__(self, id):
        super().__init__(f"Resource with ID '{id}' not found.")


class ResourceAlreadyExistsError(Exception):
    def __init__(self, id):
        super().__init__(f"Resource with ID '{id}' already exists.")


class FileHandler(BaseModel):
    @abstractmethod
    def load(self) -> Dict:
        raise NotImplementedError()

    @abstractmethod
    def save(self) -> None:
        raise NotImplementedError()


class LocalFileHandler(FileHandler):
    path: str

    def load(self) -> Dict:
        with open(self.path, "r") as fp:
            return json.load(fp)

    def save(self, state_data: Dict) -> None:
        with open(self.path, "w") as fp:
            json.dump(state_data, fp)


class S3FileHandler(FileHandler):
    bucket: str
    key: str

    _settings: BaseSettings = PrivateAttr()
    _client = PrivateAttr()

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
    """
    Represents the state data with Pydantic properties for serialization.

    # NOTE: Pydantic properties declared here will be included in the statefile.
    Make sure to update them when necessary (i.e 'last_modified')

    Attributes:
        resource_map (Dict): A dictionary to store resource data.

    Methods:
        get(id: str) -> Dict:
            Retrieve resource data based on the provided ID.

        add(id: str, data: Dict) -> None:
            Add new resource data with the specified ID.

        delete(id: str) -> None:
            Delete resource data associated with the given ID.

        update(id: str, data: Dict) -> None:
            Update resource data for the specified ID.

    Raises:
        UnexistingResourceException: Raised when attempting to access or update
                                     a non-existing resource.
        ResourceAlreadyExistsError: Raised when trying to add a resource with
                                    an ID that already exists in the resource map.
    """

    resource_map: Dict = {}

    def get(self, id: str) -> Dict:
        if id not in self.resource_map:
            raise UnexistingResourceException(id)
        return self.resource_map[id]

    def add(self, id: str, data: Dict) -> None:
        if not id in self.resource_map:
            self.resource_map[id] = data
        else:
            raise ResourceAlreadyExistsError()

    def delete(self, id: str) -> None:
        if id in self.resource_map:
            del self.resource_map[id]
        else:
            raise UnexistingResourceException(id)

    def update(self, id: str, data: Dict) -> None:
        if id not in self.resource_map:
            raise UnexistingResourceException(id)
        self.resource_map[id] = data


class State(StateData):
    """
    Represents the solution's state by maintaining a mapping of each managed resource,
    facilitating seamless manipulation and control of these resources.

    Args:
        uri (str): Storage location (S3 url or local path).
    """

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
