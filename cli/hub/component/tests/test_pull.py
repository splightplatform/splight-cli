import os
import shutil
from unittest.mock import mock_open, patch

# from remote_splight_lib.hub import SplightHubClient

from cli.hub.component.exceptions import ComponentDirectoryAlreadyExists
from cli.hub.component.hub_manager import HubComponentManager
from cli.tests.test_generic import SplightCLITest


class TestPull(SplightCLITest):
    def setUp(self):
        super().setUp()
        self.configure()
        self._manager = HubComponentManager(
            client=self.context.framework.setup.HUB_CLIENT()
        )

    # @patch.object(
    #     SplightHubClient, "download", return_value=(b"file content", 200)
    # )
    @patch("remote_splight_lib.hub.SplightHubClient.download", return_value=(b"file content", 200))
    @patch("builtins.open", new_callable=mock_open())
    @patch("py7zr.SevenZipFile")
    @patch("shutil.move", return_value=None)
    def test_pull(self, mock1, mock2, mock3, mock4):
        self._manager.pull(self.name, self.version)
        mock3.assert_called_once()
        mock2.assert_called_once()
        path = f"{self.name}/{self.version}"
        file_name = f"{self.name}-{self.version}"
        mock1.assert_called_with(file_name, path)

    def test_pull_already_exists_in_local(self):
        component_path = os.path.join(".", f"{self.name}/{self.version}")
        os.makedirs(component_path)
        with self.assertRaises(ComponentDirectoryAlreadyExists):
            self._manager.pull(self.name, self.version)
        shutil.rmtree(component_path)
