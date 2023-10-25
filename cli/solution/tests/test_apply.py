import unittest

import pytest
from mock import patch
from splight_lib.models import Asset
from splight_lib.models.base import SplightDatabaseBaseModel

from cli.solution.apply_exec import UndefinedID
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
        assert solution_manager._state.assets[0].id == asset.id
        new_component = solution_manager._state.components[0]
        assert new_component.id == component.id
        assert new_component.routines[0].id == routine.id

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
        self._retrieve_mock.assert_called_once()
        self._save_mock.assert_called_once()
        new_routine = solution_manager._state.components[0].routines[0]
        assert new_routine.id == routine.id

    def test_asset_modification_saves_remote(self):
        state = get_state()
        state["assets"][0]["name"] = "some_other_name"
        plan = get_plan()
        plan["assets"][0]["name"] = "some_other_name"

        self._confirm_mock.return_value = True
        self._load_yaml_mock.side_effect = [plan, state]

        asset = Asset.parse_obj(get_state()["assets"][0])
        component = Component.parse_obj(get_state()["components"][0])
        routine = RoutineObject.parse_obj(
            get_state()["components"][0]["routines"][0]
        )
        self._list_mock.side_effect = [[asset], [component], [routine]]

        solution_manager = SolutionManager(
            "./dummy_path", "./dummy_path", apply=True
        )
        solution_manager.execute()

        self._save_yaml_mock.assert_called_once()
        assert self._list_mock.call_count == 3
        assert self._save_mock.call_count == 0
        assert solution_manager._state.assets[0] == asset

    def test_asset_modification_saves_local(self):
        state = get_state()
        state["assets"][0]["name"] = "some_other_name"
        plan = get_plan()
        plan["assets"][0]["name"] = "some_other_name"

        self._confirm_mock.side_effect = [False, True]
        self._load_yaml_mock.side_effect = [plan, state]

        asset = Asset.parse_obj(get_state()["assets"][0])
        component = Component.parse_obj(get_state()["components"][0])
        routine = RoutineObject.parse_obj(
            get_state()["components"][0]["routines"][0]
        )
        self._list_mock.side_effect = [[asset], [component], [routine]]

        solution_manager = SolutionManager(
            "./dummy_path", "./dummy_path", apply=True
        )
        solution_manager.execute()

        self._save_yaml_mock.assert_called_once()
        assert self._list_mock.call_count == 3
        self._save_mock.assert_called_once()
        new_asset_saved = Asset.parse_obj(state["assets"][0])
        assert solution_manager._state.assets[0] == new_asset_saved

    def test_remote_asset_was_deleted(self):
        state = get_state()

        self._confirm_mock.return_value = True
        self._load_yaml_mock.side_effect = [get_plan(), state]

        asset = Asset.parse_obj(get_state()["assets"][0])
        asset.id = "643385e1-acb9-4348-befc-4686baa99d24"
        component = Component.parse_obj(get_state()["components"][0])
        routine = RoutineObject.parse_obj(
            get_state()["components"][0]["routines"][0]
        )
        self._list_mock.side_effect = [[], [component], [routine]]
        self._retrieve_mock.side_effect = [asset]

        with pytest.raises(UndefinedID):
            solution_manager = SolutionManager(
                "./dummy_path", "./dummy_path", apply=True
            )
            solution_manager.execute()

        self._save_yaml_mock.assert_called_once()
        self._list_mock.assert_called_once()
        self._retrieve_mock.assert_called_once()
        self._save_mock.assert_called_once()
        assert solution_manager._state.assets[0] == asset
