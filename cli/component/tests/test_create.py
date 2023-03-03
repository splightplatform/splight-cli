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
        shutil.rmtree(self.custompath)
        super().tearDown()

    def test_create_on_custom_path(self):
        self.component.create(self.name, self.version, self.custompath)
        for filename in ComponentLoader.REQUIRED_FILES:
            self.assertTrue(
                os.path.exists(os.path.join(self.custompath, filename))
            )

    def test_create_already_exists(self):
        os.makedirs(self.custompath)
        self.component.create(self.name, self.version, self.custompath)

        for filename in ComponentLoader.REQUIRED_FILES:
            self.assertTrue(
                os.path.exists(os.path.join(self.custompath, filename))
            )
