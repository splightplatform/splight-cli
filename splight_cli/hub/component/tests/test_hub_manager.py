import os
from unittest.mock import mock_open, patch
from uuid import uuid4

import pytest
from splight_lib.models import HubComponent

from splight_cli.component import ComponentManager
from splight_cli.hub.component.exceptions import (
    ComponentAlreadyExists,
    HubComponentNotFound,
    SpecFormatError,
    SpecValidationError,
)
from splight_cli.hub.component.hub_manager import HubComponentManager

BASE_PATH = os.getcwd()
TEST_COMPONENT_PATH = os.path.join(
    BASE_PATH, "splight_cli/tests/test_component/"
)
with open(os.path.join(TEST_COMPONENT_PATH, "spec.json"), "r") as fid:
    HUB_COMPONENT = HubComponent.model_validate_json(fid.read())
HUB_COMPONENT.id = str(uuid4())


@patch.object(ComponentManager, "test", return_value=None)
@patch.object(HubComponentManager, "_exists_in_hub", return_value=False)
def test_push(mock_exists, mock_component_manager):
    manager = HubComponentManager()
    test_component_path = os.path.join(
        os.getcwd(), "splight_cli/tests/test_component/"
    )
    with patch.object(
        HubComponent, "upload", return_value=HUB_COMPONENT
    ) as mock_hub:
        manager.push(test_component_path)
        mock_hub.assert_called_with(test_component_path)


@patch.object(ComponentManager, "test", return_value=None)
@patch(
    "splight_cli.hub.component.hub_manager.json.load", side_effect=Exception
)
def test_push_spec_format_error(mock_exists, mock_json_load):
    manager = HubComponentManager()
    test_component_path = os.path.join(
        os.getcwd(), "splight_cli/tests/test_component/"
    )
    with pytest.raises(SpecFormatError):
        manager.push(test_component_path, force=False)


@patch.object(ComponentManager, "test", return_value=None)
@patch(
    "splight_cli.hub.component.hub_manager.json.load",
    return_value={"name": "mycomponent", "splight_lib_version": "1.1.0"},
)
def test_push_spec_missing_keys(mock_exists, mock_json_load):
    manager = HubComponentManager()
    test_component_path = os.path.join(
        os.getcwd(), "splight_cli/tests/test_component/"
    )
    with pytest.raises(SpecValidationError):
        manager.push(test_component_path, force=False)


@patch.object(ComponentManager, "test", return_value=None)
@patch(
    "splight_cli.hub.component.hub_manager.json.load",
    return_value={
        "name": "mycomponent",
        "version": "0.1.0",
        "splight_lib_version": "3.0.0",
        "input": "wrong_input_type",
    },
)
def test_push_spec_wrong_attr_type(mock_exists, mock_json_load):
    manager = HubComponentManager()
    test_component_path = os.path.join(
        os.getcwd(), "splight_cli/tests/test_component/"
    )
    with pytest.raises(SpecValidationError):
        manager.push(test_component_path, force=False)


@patch.object(ComponentManager, "test", return_value=None)
@patch.object(HubComponentManager, "_exists_in_hub", return_value=True)
def test_push_already_exists(mock_exists, mock_component_manager):
    manager = HubComponentManager()
    test_component_path = os.path.join(
        os.getcwd(), "splight_cli/tests/test_component/"
    )
    with pytest.raises(ComponentAlreadyExists):
        manager.push(test_component_path, force=False)


@patch.object(ComponentManager, "test", return_value=None)
@patch.object(HubComponentManager, "_exists_in_hub", return_value=True)
def test_push_already_exists_with_force(mock_exists, mock_component_manager):
    manager = HubComponentManager()
    test_component_path = os.path.join(
        os.getcwd(), "splight_cli/tests/test_component/"
    )
    with patch.object(
        HubComponent, "upload", return_value=HUB_COMPONENT
    ) as mock_hub:
        manager.push(test_component_path, force=True)
        mock_hub.assert_called_with(test_component_path)


@patch.object(HubComponent, "list_mine", return_value=[HUB_COMPONENT])
@patch.object(HubComponent, "download", return_value=b"This is a component")
@patch("builtins.open", new_callable=mock_open())
@patch("py7zr.SevenZipFile")
@patch("shutil.move", return_value=None)
def test_pull(mock_move, mock_zip, mock_open, mock_download, mock_list):
    manager = HubComponentManager()
    manager.pull(name="TestComponent", version="1.1.0")


@patch.object(HubComponent, "list_mine", return_value=[])
def test_pull_not_found(mock_list):
    manager = HubComponentManager()
    with pytest.raises(HubComponentNotFound):
        manager._pull_component(name="TestComponent", version="1.1.0")
