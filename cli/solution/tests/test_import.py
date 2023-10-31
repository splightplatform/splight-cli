import pytest
from mock import patch
from splight_lib.models import Asset
from splight_lib.models.base import SplightDatabaseBaseModel

from cli.solution.models import Component, RoutineObject
from cli.solution.solution import SolutionManager
from cli.solution.tests.constants import get_plan, get_state


@patch("typer.confirm")
@patch("cli.solution.solution.load_yaml")
@patch("cli.solution.solution.save_yaml")
@patch.object(SplightDatabaseBaseModel, "list")
@patch.object(SplightDatabaseBaseModel, "retrieve")
@patch.object(SplightDatabaseBaseModel, "save")
def test_import_asset_correctly(
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
    asset = Asset.parse_obj(get_state()["assets"][0])
    component = Component.parse_obj(get_state()["components"][0])
    routine = RoutineObject.parse_obj(
        get_state()["components"][0]["routines"][0]
    )
    retrieve_mock.side_effect = [asset, component, routine]

    solution_manager = SolutionManager(
        "./dummy_path", "./dummy_path", apply=True
    )
    solution_manager.execute()

    save_yaml_mock.assert_called()
    assert retrieve_mock.call_count == 3
    assert save_mock.call_count == 3
    assert solution_manager._state.assets[0].id == asset.id
    new_component = solution_manager._state.components[0]
    assert new_component.id == component.id
    assert new_component.routines[0].id == routine.id
