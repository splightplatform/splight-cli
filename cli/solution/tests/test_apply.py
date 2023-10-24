from mock import patch
from splight_lib.models import Asset
from splight_lib.models.base import SplightDatabaseBaseModel

from cli.solution.models import Component, RoutineObject
from cli.solution.solution import SolutionManager
from cli.solution.tests.constants import TEST_PLAN, TEST_STATE_FILLED


@patch.object(SplightDatabaseBaseModel, "save")
@patch.object(SplightDatabaseBaseModel, "retrieve")
@patch.object(SplightDatabaseBaseModel, "list")
@patch("cli.solution.solution.save_yaml")
@patch("cli.solution.solution.load_yaml")
@patch("typer.confirm")
def test_apply_everything(
    confirm_patch,
    load_yaml_patch,
    save_yaml_patch,
    list_patch,
    retrieve_patch,
    save_patch,
):
    state = TEST_PLAN.copy()

    confirm_patch.return_value = True
    load_yaml_patch.side_effect = [TEST_PLAN, state]
    asset = Asset.parse_obj(TEST_STATE_FILLED["assets"][0])
    component = Component.parse_obj(TEST_STATE_FILLED["components"][0])
    routine = RoutineObject.parse_obj(
        TEST_STATE_FILLED["components"][0]["routines"][0]
    )
    retrieve_patch.side_effect = [asset, component, routine]

    solution_manager = SolutionManager(
        "./dummy_path", "./dummy_path", apply=True
    )
    solution_manager.execute()

    save_yaml_patch.assert_called()
    assert retrieve_patch.call_count == 3
    assert save_patch.call_count == 3


@patch.object(SplightDatabaseBaseModel, "save")
@patch.object(SplightDatabaseBaseModel, "retrieve")
@patch.object(SplightDatabaseBaseModel, "list")
@patch("cli.solution.solution.save_yaml")
@patch("cli.solution.solution.load_yaml")
@patch("typer.confirm")
def test_apply_remote_asset_component_create(
    confirm_patch,
    load_yaml_patch,
    save_yaml_patch,
    list_patch,
    retrieve_patch,
    save_patch,
):
    state = TEST_PLAN.copy()
    state["assets"] = TEST_STATE_FILLED["assets"].copy()

    confirm_patch.return_value = True
    load_yaml_patch.side_effect = [TEST_PLAN, state]

    asset = Asset.parse_obj(TEST_STATE_FILLED["assets"][0])
    component = Component.parse_obj(TEST_STATE_FILLED["components"][0])
    routine = RoutineObject.parse_obj(
        TEST_STATE_FILLED["components"][0]["routines"][0]
    )
    retrieve_patch.side_effect = [component, routine]
    list_patch.side_effect = [[asset]]

    solution_manager = SolutionManager(
        "./dummy_path", "./dummy_path", apply=True
    )
    solution_manager.execute()

    save_yaml_patch.assert_called()
    list_patch.assert_called_once()
    assert retrieve_patch.call_count == 2
    assert save_patch.call_count == 2
