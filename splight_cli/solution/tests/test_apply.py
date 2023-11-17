import pytest
from mock import patch
from splight_lib.models import Asset, RoutineObject
from splight_lib.models.base import SplightDatabaseBaseModel

from splight_cli.solution.models import Component
from splight_cli.solution.solution import SolutionManager
from splight_cli.solution.tests.constants import get_plan, get_state


@patch("typer.confirm")
@patch("splight_cli.solution.solution.load_yaml")
@patch("splight_cli.solution.solution.save_yaml")
@patch.object(SplightDatabaseBaseModel, "list")
@patch.object(SplightDatabaseBaseModel, "retrieve")
@patch.object(SplightDatabaseBaseModel, "save")
def test_apply_everything(
    save_mock,
    retrieve_mock,
    list_mock,
    save_yaml_mock,
    load_yaml_mock,
    confirm_mock,
):
    state = get_plan()

    confirm_mock.return_value = True
    load_yaml_mock.side_effect = [get_plan(), state]
    asset = Asset.model_validate(get_state()["assets"][0])
    component = Component.model_validate(get_state()["components"][0])
    routine = RoutineObject.model_validate(
        get_state()["components"][0]["routines"][0]
    )
    retrieve_mock.side_effect = [asset, component, routine]

    solution_manager = SolutionManager("./dummy_path", "./dummy_path")
    solution_manager.apply()

    save_yaml_mock.assert_called()
    assert retrieve_mock.call_count == 3
    assert save_mock.call_count == 3
    assert solution_manager._state.assets[0].id == asset.id
    new_component = solution_manager._state.components[0]
    assert new_component.id == component.id
    assert new_component.routines[0].id == routine.id


@patch("typer.confirm")
@patch("splight_cli.solution.solution.load_yaml")
@patch("splight_cli.solution.solution.save_yaml")
@patch.object(SplightDatabaseBaseModel, "list")
@patch.object(SplightDatabaseBaseModel, "retrieve")
@patch.object(SplightDatabaseBaseModel, "save")
def test_apply_remote_asset_create_component(
    save_mock,
    retrieve_mock,
    list_mock,
    save_yaml_mock,
    load_yaml_mock,
    confirm_mock,
):
    state = get_plan()
    state["assets"] = get_state()["assets"]

    confirm_mock.return_value = True
    load_yaml_mock.side_effect = [get_plan(), state]

    asset = Asset.model_validate(get_state()["assets"][0])
    component = Component.model_validate(get_state()["components"][0])
    routine = RoutineObject.model_validate(
        get_state()["components"][0]["routines"][0]
    )
    retrieve_mock.side_effect = [component, routine]
    list_mock.side_effect = [[asset]]

    solution_manager = SolutionManager("./dummy_path", "./dummy_path")
    solution_manager.apply()

    save_yaml_mock.assert_called()
    list_mock.assert_called_once()
    assert retrieve_mock.call_count == 2
    assert save_mock.call_count == 2
    new_component = solution_manager._state.components[0]
    assert new_component.id == component.id
    assert new_component.routines[0].id == routine.id


@patch("typer.confirm")
@patch("splight_cli.solution.solution.load_yaml")
@patch("splight_cli.solution.solution.save_yaml")
@patch.object(SplightDatabaseBaseModel, "list")
@patch.object(SplightDatabaseBaseModel, "retrieve")
@patch.object(SplightDatabaseBaseModel, "save")
def test_apply_remote_asset_create_routine(
    save_mock,
    retrieve_mock,
    list_mock,
    save_yaml_mock,
    load_yaml_mock,
    confirm_mock,
):
    state = get_state()
    empty_routine = get_plan()["components"][0]["routines"][0]
    state["components"][0]["routines"][0] = empty_routine

    confirm_mock.return_value = True
    load_yaml_mock.side_effect = [get_plan(), state]

    asset = Asset.model_validate(get_state()["assets"][0])
    component = Component.model_validate(get_state()["components"][0])
    routine = RoutineObject.model_validate(
        get_state()["components"][0]["routines"][0]
    )
    retrieve_mock.side_effect = [routine]
    list_mock.side_effect = [[asset], [component]]

    solution_manager = SolutionManager("./dummy_path", "./dummy_path")
    solution_manager.apply()

    save_yaml_mock.assert_called()
    assert list_mock.call_count == 2
    retrieve_mock.assert_called_once()
    save_mock.assert_called_once()
    new_routine = solution_manager._state.components[0].routines[0]
    assert new_routine.id == routine.id


@patch("typer.confirm")
@patch("splight_cli.solution.solution.load_yaml")
@patch("splight_cli.solution.solution.save_yaml")
@patch.object(SplightDatabaseBaseModel, "list")
@patch.object(SplightDatabaseBaseModel, "retrieve")
@patch.object(SplightDatabaseBaseModel, "save")
def test_asset_modification_saves_remote(
    save_mock,
    retrieve_mock,
    list_mock,
    save_yaml_mock,
    load_yaml_mock,
    confirm_mock,
):
    state = get_state()
    state["assets"][0]["name"] = "some_other_name"
    plan = get_plan()
    plan["assets"][0]["name"] = "some_other_name"

    confirm_mock.return_value = True
    load_yaml_mock.side_effect = [plan, state]

    asset = Asset.model_validate(get_state()["assets"][0])
    component = Component.model_validate(get_state()["components"][0])
    routine = RoutineObject.model_validate(
        get_state()["components"][0]["routines"][0]
    )
    list_mock.side_effect = [[asset], [component], [routine]]

    solution_manager = SolutionManager("./dummy_path", "./dummy_path")
    solution_manager.apply()

    assert save_yaml_mock.call_count == 2
    assert list_mock.call_count == 3
    assert save_mock.call_count == 0
    assert solution_manager._state.assets[0].name == asset.name


@patch("typer.confirm")
@patch("splight_cli.solution.solution.load_yaml")
@patch("splight_cli.solution.solution.save_yaml")
@patch.object(SplightDatabaseBaseModel, "list")
@patch.object(SplightDatabaseBaseModel, "retrieve")
@patch.object(SplightDatabaseBaseModel, "save")
def test_routine_modification_saves_local(
    save_mock,
    retrieve_mock,
    list_mock,
    save_yaml_mock,
    load_yaml_mock,
    confirm_mock,
):
    state = get_state()
    plan = get_plan()
    routine = plan["components"][0]["routines"][0]
    routine["config"][0]["value"] = 22

    confirm_mock.side_effect = [False, True]
    load_yaml_mock.side_effect = [plan, state]

    asset = Asset.model_validate(get_state()["assets"][0])
    component = Component.model_validate(get_state()["components"][0])
    routine = RoutineObject.model_validate(
        get_state()["components"][0]["routines"][0]
    )
    list_mock.side_effect = [[asset], [component], [routine]]
    retrieve_mock.side_effect = [RoutineObject.model_validate(routine)]

    solution_manager = SolutionManager("./dummy_path", "./dummy_path")
    solution_manager.apply()

    save_yaml_mock.assert_called_once()
    assert list_mock.call_count == 3
    save_mock.assert_called_once()
    config_val = (
        solution_manager._state.components[0].routines[0].config[0].value
    )
    assert config_val == routine.config[0].value


@patch("typer.confirm")
@patch("splight_cli.solution.solution.load_yaml")
@patch("splight_cli.solution.solution.save_yaml")
@patch.object(SplightDatabaseBaseModel, "list")
@patch.object(SplightDatabaseBaseModel, "retrieve")
@patch.object(SplightDatabaseBaseModel, "save")
def test_remote_asset_was_deleted(
    save_mock,
    retrieve_mock,
    list_mock,
    save_yaml_mock,
    load_yaml_mock,
    confirm_mock,
):
    state = get_state()

    confirm_mock.side_effect = [True, True]
    load_yaml_mock.side_effect = [get_plan(), state]

    asset = Asset.model_validate(get_state()["assets"][0])
    asset.id = "643385e1-acb9-4348-befc-4686baa99d24"
    component = Component.model_validate(get_state()["components"][0])
    routine = RoutineObject.model_validate(
        get_state()["components"][0]["routines"][0]
    )
    list_mock.side_effect = [[], [component], [routine]]
    retrieve_mock.side_effect = [asset]

    solution_manager = SolutionManager("./dummy_path", "./dummy_path")
    solution_manager.apply()

    assert save_yaml_mock.call_count == 2
    assert list_mock.call_count == 3
    retrieve_mock.assert_called_once()
    save_mock.assert_called_once()
    assert solution_manager._state.assets[0].name == asset.name
    assert solution_manager._state.assets[0].id == asset.id
