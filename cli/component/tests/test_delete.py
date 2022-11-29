import os
from unittest.mock import patch


from cli.component.component import Component
from cli.component.handler import ComponentHandler
from cli.tests.test_generic import SplightCLITest


class TestDelete(SplightCLITest):
    def setUp(self):
        super().setUp()
        self.original_component_path = self.path
        self.path = os.path.dirname(os.path.abspath(__file__))
        self.extracted_component_path = os.path.join(
            self.path, f"{self.name}-{self.version}"
        )
        self.component = Component(self.path, self.context)

    def test_component_delete(self):
        with patch.object(
            ComponentHandler, "delete_component"
        ) as call:
            self.component.delete(self.name, self.version)
            call.assert_called_with(
                self.name, self.version
            )