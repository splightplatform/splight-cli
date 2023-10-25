import unittest

import pytest
from mock import patch
from splight_lib.models import Asset
from splight_lib.models.base import SplightDatabaseBaseModel

from cli.solution.models import Component, RoutineObject
from cli.solution.solution import SolutionManager
from cli.solution.tests.constants import get_plan, get_state


class TestApply(unittest.TestCase):
    def setUp(self):
        self._confirm_mock = patch("typer.confirm").start()
        self._load_yaml_mock = patch("cli.solution.solution.load_yaml").start()
        self._save_yaml_mock = patch("cli.solution.solution.save_yaml").start()
        self._list_mock = patch.object(
            SplightDatabaseBaseModel, "list"
        ).start()
        self._retrieve_mock = patch.object(
            SplightDatabaseBaseModel, "retrieve"
        ).start()
        self._save_mock = patch.object(
            SplightDatabaseBaseModel, "save"
        ).start()

    # @pytest.mark.skip(reason="no reason")
    def test_apply_everything(self):
        state = get_plan()

        self._confirm_mock.return_value = True
        self._load_yaml_mock.side_effect = [get_plan(), state]
        asset = Asset.parse_obj(get_state()["assets"][0])
        component = Component.parse_obj(get_state()["components"][0])
        routine = RoutineObject.parse_obj(
            get_state()["components"][0]["routines"][0]
        )
        self._retrieve_mock.side_effect = [asset, component, routine]

        solution_manager = SolutionManager(
            "./dummy_path", "./dummy_path", apply=True
        )
        solution_manager.execute()

        self._save_yaml_mock.assert_called()
        assert self._retrieve_mock.call_count == 3
        assert self._save_mock.call_count == 3

    # @pytest.mark.skip(reason="no reason")
    def test_apply_remote_asset_create_component(self):
        state = get_plan()
        state["assets"] = get_state()["assets"]

        self._confirm_mock.return_value = True
        self._load_yaml_mock.side_effect = [get_plan(), state]

        asset = Asset.parse_obj(get_state()["assets"][0])
        component = Component.parse_obj(get_state()["components"][0])
        routine = RoutineObject.parse_obj(
            get_state()["components"][0]["routines"][0]
        )
        self._retrieve_mock.side_effect = [component, routine]
        self._list_mock.side_effect = [[asset]]

        solution_manager = SolutionManager(
            "./dummy_path", "./dummy_path", apply=True
        )
        solution_manager.execute()

        self._save_yaml_mock.assert_called()
        self._list_mock.assert_called_once()
        assert self._retrieve_mock.call_count == 2
        assert self._save_mock.call_count == 2
        new_component = solution_manager._state.components[0]
        assert new_component.id == component.id
        assert new_component.routines[0].id == routine.id

    def test_apply_remote_asset_create_routine(self):
        state = get_state()
        empty_routine = get_plan()["components"][0]["routines"][0]
        state["components"][0]["routines"][0] = empty_routine

        self._confirm_mock.return_value = True
        self._load_yaml_mock.side_effect = [get_plan(), state]

        asset = Asset.parse_obj(get_state()["assets"][0])
        component = Component.parse_obj(get_state()["components"][0])
        routine = RoutineObject.parse_obj(
            get_state()["components"][0]["routines"][0]
        )
        self._retrieve_mock.side_effect = [routine]
        self._list_mock.side_effect = [[asset], [component]]

        solution_manager = SolutionManager(
            "./dummy_path", "./dummy_path", apply=True
        )
        solution_manager.execute()

        self._save_yaml_mock.assert_called()
        assert self._list_mock.call_count == 2
        assert self._retrieve_mock.call_count == 1
        assert self._save_mock.call_count == 1
        new_routine = solution_manager._state.components[0].routines[0]
        assert new_routine.id == routine.id

    def test_apply_remote_asset_create_routine(self):
        state = get_state()
        empty_routine = get_plan()["components"][0]["routines"][0]
        state["components"][0]["routines"][0] = empty_routine

        self._confirm_mock.return_value = True
        self._load_yaml_mock.side_effect = [get_plan(), state]

        asset = Asset.parse_obj(get_state()["assets"][0])
        component = Component.parse_obj(get_state()["components"][0])
        routine = RoutineObject.parse_obj(
            get_state()["components"][0]["routines"][0]
        )
        self._retrieve_mock.side_effect = [routine]
        self._list_mock.side_effect = [[asset], [component]]

        solution_manager = SolutionManager(
            "./dummy_path", "./dummy_path", apply=True
        )
        solution_manager.execute()

        self._save_yaml_mock.assert_called()
        assert self._list_mock.call_count == 2
        assert self._retrieve_mock.call_count == 1
        assert self._save_mock.call_count == 1
        new_routine = solution_manager._state.components[0].routines[0]
        assert new_routine.id == routine.id
