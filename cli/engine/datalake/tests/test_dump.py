from unittest.mock import patch

from cli.engine.datalake import datalake_app
from cli.engine.manager import DatalakeManager
from cli.tests.test_generic import SplightCLITest


class TestDump(SplightCLITest):
    def setUp(self):
        super().setUp()
        self.configure()

    def test_dump(self):
        with patch.object(DatalakeManager, "dump") as mocked_dump:
            _ = self.runner.invoke(
                datalake_app,
                ["dump", "collection"],
                obj=self.context,
                catch_exceptions=False,
                env={
                    "SPLIGHT_ACCESS_ID": "access_id",
                    "SPLIGHT_SECRET_KEY": "secret_key",
                }
            )
            mocked_dump.assert_called_once()
