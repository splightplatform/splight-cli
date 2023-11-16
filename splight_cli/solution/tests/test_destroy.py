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
@patch.object(SplightDatabaseBaseModel, "delete")
def test_no_id_no_destroy(
    delete_mock,
    save_yaml_mock,
    load_yaml_mock,
    confirm_mock,
):
    state = get_plan()
    plan = get_plan()
    load_yaml_mock.side_effect = [plan, state]

    solution_manager = SolutionManager("./dummy_path", "./dummy_path")
    solution_manager.destroy()

    delete_mock.assert_not_called()
    save_yaml_mock.assert_not_called()
    assert len(solution_manager._state.assets) == len(get_plan()["assets"])
    assert len(solution_manager._state.components) == len(
        get_plan()["components"]
    )


@patch("typer.confirm")
@patch("splight_cli.solution.solution.load_yaml")
@patch("splight_cli.solution.solution.save_yaml")
@patch.object(SplightDatabaseBaseModel, "delete")
def test_destroy_everything(
    delete_mock,
    save_yaml_mock,
    load_yaml_mock,
    confirm_mock,
):
    state = get_state()
    plan = get_plan()
    load_yaml_mock.side_effect = [plan, state]
    confirm_mock.return_value = True

    solution_manager = SolutionManager("./dummy_path", "./dummy_path")
    solution_manager.destroy()

    assert delete_mock.call_count == 2
    assert save_yaml_mock.call_count == 2
    assert not len(solution_manager._state.assets)
    assert not len(solution_manager._state.components)


@patch("typer.confirm")
@patch("splight_cli.solution.solution.load_yaml")
@patch("splight_cli.solution.solution.save_yaml")
@patch.object(SplightDatabaseBaseModel, "delete")
def test_destroy_only_the_asset(
    delete_mock,
    save_yaml_mock,
    load_yaml_mock,
    confirm_mock,
):
    state = get_state()
    plan = get_plan()
    load_yaml_mock.side_effect = [plan, state]
    confirm_mock.side_effect = [True, False]

    solution_manager = SolutionManager("./dummy_path", "./dummy_path")
    solution_manager.destroy()

    delete_mock.assert_called_once()
    save_yaml_mock.assert_called_once()
    assert not len(solution_manager._state.assets)
    assert len(solution_manager._state.components) == len(
        get_plan()["components"]
    )


@patch("typer.confirm")
@patch("splight_cli.solution.solution.load_yaml")
@patch("splight_cli.solution.solution.save_yaml")
@patch.object(SplightDatabaseBaseModel, "delete")
def test_destroy_only_the_component(
    delete_mock,
    save_yaml_mock,
    load_yaml_mock,
    confirm_mock,
):
    state = get_state()
    plan = get_plan()
    load_yaml_mock.side_effect = [plan, state]
    confirm_mock.side_effect = [False, True]

    solution_manager = SolutionManager("./dummy_path", "./dummy_path")
    solution_manager.destroy()

    delete_mock.assert_called_once()
    save_yaml_mock.assert_called_once()
    assert len(solution_manager._state.assets) == len(get_plan()["assets"])
    assert not len(solution_manager._state.components)
