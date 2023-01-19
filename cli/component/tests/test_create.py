import os
import shutil
from cli.component.loaders import ComponentLoader
from cli.component.component import Component
from cli.tests.test_generic import SplightCLITest


class TestCreate(SplightCLITest):
    def setUp(self):
        super().setUp()
        self.component = Component(self.context)

    def tearDown(self) -> None:
        shutil.rmtree(self.name)
        super().tearDown()

    def test_create(self):
        self.component.create(self.name, self.version)
        for filename in ComponentLoader.REQUIRED_FILES:
            self.assertTrue(
                os.path.exists(os.path.join(self.name, self.version, filename))
            )

    def test_create_already_exists(self):
        os.makedirs(os.path.join(self.name, self.version))
        with self.assertRaises(Exception):
            self.component.create(self.name, self.version)
