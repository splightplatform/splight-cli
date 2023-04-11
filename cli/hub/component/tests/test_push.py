from unittest.mock import patch

from cli.hub.component.hub_manager import HubComponentManager
from cli.hub.component.exceptions import ComponentAlreadyExists, ComponentTestError
from cli.tests.test_generic import SplightCLITest
from cli.component.component import Component


class TestPull(SplightCLITest):
    def setUp(self):
        super().setUp()
        self.configure()
        self._manager = HubComponentManager(
            client=self.context.framework.setup.HUB_CLIENT()
        )

    @patch("remote_splight_lib.hub.SplightHubClient.upload", return_value=None)
    @patch.object(HubComponentManager, "_exists_in_hub", return_value=False)
    @patch.object(Component, "test", return_value=True)
    def test_push_no_force(self, mock1, mock2, mock3):
        self._manager.push(path=self.path, force=False)

    @patch("remote_splight_lib.hub.SplightHubClient.upload", return_value=None)
    @patch.object(HubComponentManager, "_exists_in_hub", return_value=True)
    @patch.object(Component, "test", return_value=True)
    def test_push_exists_in_hub(self, mock1, mock2, mock3):
        with self.assertRaises(ComponentAlreadyExists):
            self._manager.push(path=self.path, force=False)

    @patch("remote_splight_lib.hub.SplightHubClient.upload", return_value=None)
    @patch.object(HubComponentManager, "_exists_in_hub", return_value=True)
    @patch.object(HubComponentManager, "_upload_component", return_value=None)
    @patch.object(Component, "test", return_value=True)
    def test_push_exists_with_force(self, mock1, mock2, mock3, mock4):
        self._manager.push(path=self.path, force=True)
        mock1.assert_called_once()

    @patch("remote_splight_lib.hub.SplightHubClient.upload", return_value=None)
    @patch.object(HubComponentManager, "_exists_in_hub", return_value=False)
    @patch.object(Component, "test", return_value=False)
    def test_push_failing_tests(self, mock1, mock2, mock3):
        with self.assertRaises(ComponentTestError):
            self._manager.push(path=self.path)
