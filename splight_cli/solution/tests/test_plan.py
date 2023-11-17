import pytest
from mock import patch
from splight_lib.models import Asset, RoutineObject
from splight_lib.models.base import SplightDatabaseBaseModel

from splight_cli.solution.exceptions import UndefinedID
from splight_cli.solution.models import Component
from splight_cli.solution.solution import SolutionManager
from splight_cli.solution.tests.constants import get_plan, get_state


@patch("splight_cli.solution.solution.save_yaml")
@patch("splight_cli.solution.solution.load_yaml")
def test_plan_print(load_yaml_mock, save_yaml_mock):
    load_yaml_mock.side_effect = [get_plan(), get_plan()]
    solution_manager = SolutionManager("./dummy_path", "./dummy_path")
    solution_manager.plan()


@patch("splight_cli.solution.solution.save_yaml")
@patch("splight_cli.solution.solution.load_yaml")
def test_plan_raise_undefined_asset_name(load_yaml_mock, save_yaml_mock):
    plan = get_plan()
    plan["components"][0]["routines"][0]["output"][0]["value"] = {
        "asset": "local.{{test_asset}}",
        "attribute": "attr_5",
    }
    load_yaml_mock.side_effect = [plan, plan]
    solution_manager = SolutionManager("./dummy_path", "./dummy_path")
    with pytest.raises(UndefinedID):
        solution_manager.plan()


@patch("splight_cli.solution.solution.save_yaml")
@patch("splight_cli.solution.solution.load_yaml")
@patch.object(SplightDatabaseBaseModel, "list")
def test_plan_diff_with_remote(list_mock, load_yaml_mock, save_yaml_mock):
    plan = get_plan()
    state = get_state()
    load_yaml_mock.side_effect = [plan, state]
    asset = Asset.model_validate(get_state()["assets"][0])
    asset.id = "9dfbd40c-1a4d-491b-a59a-0a70aae1895e"
    component = Component.model_validate(get_state()["components"][0])
    routine = RoutineObject.model_validate(
        get_state()["components"][0]["routines"][0]
    )
    list_mock.side_effect = [[asset], [component], [routine]]

    solution_manager = SolutionManager("./dummy_path", "./dummy_path")
    solution_manager.plan()

    assert list_mock.call_count == 3
