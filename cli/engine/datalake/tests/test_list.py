import os

os.environ["SPLIGHT_ACCESS_ID"] = "access_id"
os.environ["SPLIGHT_SECRET_KEY"] = "secret_key"

from unittest.mock import patch

from remote_splight_lib.database import DatabaseClient
from splight_models import Component

from cli.engine.datalake import datalake_app
from cli.tests.test_generic import SplightCLITest

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
        "remote_splight_lib.database.DatabaseClient.get",
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
