import pytest
from mock import patch
from splight_lib.client.exceptions import InstanceNotFound
from splight_lib.models import Asset, RoutineObject
from splight_lib.models.base import SplightDatabaseBaseModel

from cli.solution.models import Component
from cli.solution.solution import SolutionManager
from cli.solution.tests.constants import get_plan, get_state


@patch("cli.solution.solution.load_yaml")
@patch("cli.solution.solution.save_yaml")
@patch.object(SplightDatabaseBaseModel, "retrieve")
def test_import_asset_correctly(retrieve_mock, save_yaml_mock, load_yaml_mock):
    state = get_plan()
    plan = get_plan()
    load_yaml_mock.side_effect = [plan, state]
    asset = Asset.parse_obj(get_state()["assets"][0])

    retrieve_mock.side_effect = [asset]

    solution_manager = SolutionManager(
        "./dummy_path", "./dummy_path", apply=True
    )
    solution_manager.import_element(
        "asset", "f1aefe25-ac8d-490e-8ad1-21d3a3de0c08"
    )

    assert save_yaml_mock.call_count == 2
    retrieve_mock.assert_called_once()
    assert solution_manager._state.imported_assets[0] == asset


@patch("cli.solution.solution.load_yaml")
@patch("cli.solution.solution.save_yaml")
@patch.object(SplightDatabaseBaseModel, "retrieve")
def test_already_imported_asset(retrieve_mock, save_yaml_mock, load_yaml_mock):
    state = get_state()
    plan = get_plan()
    load_yaml_mock.side_effect = [plan, state]
    asset = Asset.parse_obj(get_state()["assets"][0])

    retrieve_mock.side_effect = [asset]

    solution_manager = SolutionManager(
        "./dummy_path", "./dummy_path", apply=True
    )
    solution_manager.import_element(
        "asset", "f1aefe25-ac8d-490e-8ad1-21d3a3de0c08"
    )

    save_yaml_mock.assert_not_called()
    retrieve_mock.assert_not_called()
    assert not solution_manager._state.imported_assets


@patch("cli.solution.solution.load_yaml")
@patch("cli.solution.solution.save_yaml")
@patch.object(SplightDatabaseBaseModel, "retrieve")
def test_asset_not_in_db(retrieve_mock, save_yaml_mock, load_yaml_mock):
    state = get_state()
    plan = get_plan()
    load_yaml_mock.side_effect = [plan, state]

    retrieve_mock.side_effect = InstanceNotFound(
        "Asset", "g1aefe25-ac8d-490e-8ad1-21d3a3de0c08"
    )

    with pytest.raises(InstanceNotFound):
        solution_manager = SolutionManager(
            "./dummy_path", "./dummy_path", apply=True
        )
        solution_manager.import_element(
            "asset", "g1aefe25-ac8d-490e-8ad1-21d3a3de0c08"
        )

    save_yaml_mock.assert_not_called()
    retrieve_mock.assert_called_once()
    assert not solution_manager._state.imported_assets


@patch("cli.solution.solution.load_yaml")
@patch("cli.solution.solution.save_yaml")
@patch.object(SplightDatabaseBaseModel, "retrieve")
@patch.object(SplightDatabaseBaseModel, "list")
def test_import_component_correctly(
    list_mock, retrieve_mock, save_yaml_mock, load_yaml_mock
):
    state = get_plan()
    plan = get_plan()
    load_yaml_mock.side_effect = [plan, state]
    component = Component.parse_obj(get_state()["components"][0])
    routine = RoutineObject.parse_obj(
        get_state()["components"][0]["routines"][0]
    )
    retrieve_mock.side_effect = [component.copy()]
    list_mock.side_effect = [[routine.copy()]]

    solution_manager = SolutionManager(
        "./dummy_path", "./dummy_path", apply=True
    )
    solution_manager.import_element(
        "component", "5fcca841-8e80-4f5f-b941-763353c30e9b"
    )

    assert save_yaml_mock.call_count == 2
    retrieve_mock.assert_called_once()
    list_mock.assert_called_once()
    assert solution_manager._state.imported_components[0] == component


@patch("cli.solution.solution.load_yaml")
@patch("cli.solution.solution.save_yaml")
@patch.object(SplightDatabaseBaseModel, "retrieve")
@patch.object(SplightDatabaseBaseModel, "list")
def test_already_imported_component(
    list_mock, retrieve_mock, save_yaml_mock, load_yaml_mock
):
    state = get_state()
    plan = get_plan()
    load_yaml_mock.side_effect = [plan, state]
    component = Component.parse_obj(get_state()["components"][0])
    routine = RoutineObject.parse_obj(
        get_state()["components"][0]["routines"][0]
    )

    retrieve_mock.side_effect = [component.copy()]
    list_mock.side_effect = [[routine.copy()]]

    solution_manager = SolutionManager(
        "./dummy_path", "./dummy_path", apply=True
    )
    solution_manager.import_element(
        "component", "5fcca841-8e80-4f5f-b941-763353c30e9b"
    )

    save_yaml_mock.assert_not_called()
    retrieve_mock.assert_not_called()
    list_mock.assert_not_called()
    assert not solution_manager._state.imported_components


@patch("cli.solution.solution.load_yaml")
@patch("cli.solution.solution.save_yaml")
@patch.object(SplightDatabaseBaseModel, "retrieve")
def test_component_not_in_db(retrieve_mock, save_yaml_mock, load_yaml_mock):
    state = get_state()
    plan = get_plan()
    load_yaml_mock.side_effect = [plan, state]

    retrieve_mock.side_effect = InstanceNotFound(
        "Component", "g1aefe25-ac8d-490e-8ad1-21d3a3de0c08"
    )

    with pytest.raises(InstanceNotFound):
        solution_manager = SolutionManager(
            "./dummy_path", "./dummy_path", apply=True
        )
        solution_manager.import_element(
            "component", "g1aefe25-ac8d-490e-8ad1-21d3a3de0c08"
        )

    save_yaml_mock.assert_not_called()
    retrieve_mock.assert_called_once()
    assert not solution_manager._state.imported_components
