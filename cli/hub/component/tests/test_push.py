from unittest.mock import patch

from cli.hub.component.hub_manager import HubComponentManager
from cli.hub.component.exceptions import ComponentAlreadyExists
from cli.tests.test_generic import SplightCLITest


class TestPull(SplightCLITest):
    def setUp(self):
        super().setUp()
        self.configure()
        self._manager = HubComponentManager(
            client=self.context.framework.setup.HUB_CLIENT()
        )

    def test_push_no_force(self):
        self._manager.push(path=self.path, force=False)

    @patch.object(HubComponentManager, "_exists_in_hub", return_value=True)
    def test_push_exists_in_hub(self, mock1):
        with self.assertRaises(ComponentAlreadyExists):
            self._manager.push(path=self.path, force=False)

    @patch.object(HubComponentManager, "_exists_in_hub", return_value=True)
    @patch.object(HubComponentManager, "_upload_component", return_value=None)
    def test_push_exists_with_force(self, mock1, mock2):
        self._manager.push(path=self.path, force=True)
        mock1.assert_called_once()