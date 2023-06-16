import os
from unittest.mock import mock_open, patch
from uuid import uuid4

import pytest
from cli.component import ComponentManager
from cli.hub.component.exceptions import (
    ComponentAlreadyExists,
    HubComponentNotFound,
)
from cli.hub.component.hub_manager import HubComponentManager
from splight_lib.models import HubComponent

BASE_PATH = os.getcwd()
TEST_COMPONENT_PATH = os.path.join(BASE_PATH, "cli/tests/test_component/")
HUB_COMPONENT = HubComponent.parse_file(
    os.path.join(TEST_COMPONENT_PATH, "spec.json")
)
HUB_COMPONENT.id = str(uuid4())


@patch.object(ComponentManager, "test", return_value=None)
@patch.object(HubComponentManager, "_exists_in_hub", return_value=False)
def test_push(mock_exists, mock_component_manager):
    manager = HubComponentManager()
    test_component_path = os.path.join(
        os.getcwd(), "cli/tests/test_component/"
    )
    with patch.object(
        HubComponent, "upload", return_value=HUB_COMPONENT
    ) as mock_hub:
        manager.push(test_component_path)
        mock_hub.assert_called_with(test_component_path)


@patch.object(ComponentManager, "test", return_value=None)
@patch.object(HubComponentManager, "_exists_in_hub", return_value=True)
def test_push_already_exists(mock_exists, mock_component_manager):
    manager = HubComponentManager()
    test_component_path = os.path.join(
        os.getcwd(), "cli/tests/test_component/"
    )
    with pytest.raises(ComponentAlreadyExists):
        manager.push(test_component_path, force=False)


@patch.object(ComponentManager, "test", return_value=None)
@patch.object(HubComponentManager, "_exists_in_hub", return_value=True)
def test_push_already_exists_with_force(mock_exists, mock_component_manager):
    manager = HubComponentManager()
    test_component_path = os.path.join(
        os.getcwd(), "cli/tests/test_component/"
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
