import pytest
from mock import patch

from cli.solution.plan_exec import MissingDataAddress
from cli.solution.solution import SolutionManager
from cli.solution.tests.constants import (
    TEST_PLAN,
    TEST_STATE_MISSING_ADDRESS,
    TEST_STATE_MISSING_ADDRESS_2,
)


@patch("cli.solution.solution.save_yaml")
@patch("cli.solution.solution.load_yaml")
def test_plan_print(load_patch, save_patch):
    state = TEST_PLAN.copy()
    load_patch.side_effect = [TEST_PLAN, state]
    solution_manager = SolutionManager("./dummy_path", "./dummy_path")
    solution_manager.execute()


@pytest.mark.parametrize(
    "state_dict", [TEST_STATE_MISSING_ADDRESS, TEST_STATE_MISSING_ADDRESS_2]
)
@patch("cli.solution.solution.save_yaml")
@patch("cli.solution.solution.load_yaml")
def test_plan_fails(load_patch, save_patch, state_dict):
    load_patch.side_effect = [TEST_PLAN, state_dict]
    solution_manager = SolutionManager("./dummy_path", "./dummy_path")
    with pytest.raises(MissingDataAddress):
        solution_manager.execute()
