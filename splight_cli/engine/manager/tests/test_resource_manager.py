from unittest.mock import patch

import pytest
from splight_lib.models import Asset, Attribute

from splight_cli.engine.manager import (
    ResourceManager,
    ResourceManagerException,
)


@pytest.mark.parametrize(
    "model,params",
    [
        (Asset, {"name": "my_asset", "verified": False}),
        (Attribute, {"name": "my-attr"}),
    ],
)
def test_list(model, params):
    manager = ResourceManager(model)
    with patch.object(model, "list", return_value=[]) as mock:
        manager.list(params)
        mock.assert_called_with(**params)


@pytest.mark.parametrize(
    "model,id,result",
    [
        (Asset, "1234", Asset(name="my-asset")),
        (Attribute, "1234", Attribute(name="my-attr", asset="1234")),
    ],
)
def test_get(model, id, result):
    manager = ResourceManager(model)
    with patch.object(model, "retrieve", return_value=result) as mock:
        manager.get(instance_id=id)
        mock.assert_called_with(resource_id=id)


@pytest.mark.parametrize(
    "model,id,result",
    [
        (Asset, "1234", None),
        (Attribute, "1234", None),
    ],
)
def test_get_not_found(model, id, result):
    manager = ResourceManager(model)
    with patch.object(model, "retrieve", return_value=result):
        with pytest.raises(ResourceManagerException):
            manager.get(instance_id=id)


@pytest.mark.parametrize(
    "model,data",
    [
        (Asset, Asset(name="my-asset").model_dump()),
        (Attribute, Attribute(name="my-attr", asset="some_id").model_dump()),
    ],
)
def test_create(model, data):
    manager = ResourceManager(model)
    with patch.object(model, "save", return_value=None):
        manager.create(data)
