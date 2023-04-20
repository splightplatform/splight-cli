from unittest.mock import patch

from cli.engine.datalake import datalake_app
from cli.tests.test_generic import SplightCLITest
from splight_models import Component

remote_collections = [
    Component(
        id="test_id",
        name="test component",
        version="1.0.0",
        description="",
        type="",
    ),
]


class TestList(SplightCLITest):
    def setUp(self):
        super().setUp()

    @patch(
        "splight_lib.client.database.RemoteDatabaseClient.get",
        return_value=remote_collections,
    )
    def test_list(self, mock):
        result = self.runner.invoke(
            datalake_app, "list", obj=self.context, catch_exceptions=False
        )
        _stdout = result.output
        self.assertIn("Name", _stdout)
        self.assertIn("Component reference", _stdout)
        self.assertIn("default", _stdout)
        self.assertIn("-", _stdout)
