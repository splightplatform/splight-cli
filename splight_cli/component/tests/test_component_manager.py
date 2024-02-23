import os
from dataclasses import dataclass
from unittest.mock import call, mock_open, patch

from splight_lib.component.spec import Spec

from splight_cli.component.component import ComponentManager

COMPONENT_PATH = "./splight_cli/tests/test_component/"
COMPONENT_FILES = [
    "Initialization",
    "README.md",
    "spec.json",
    ".splightignore",
    "tests.py",
]

SPEC = Spec.model_validate(
    {
        "name": "TestComponent",
        "version": "0.1.0",
        "splight_lib_version": "1.1.1",
        "privacy_policy": "public",
        "component_type": "algorithm",
        "custom_types": [],
        "input": [
            {"name": "Int", "type": "int", "required": True, "value": 1},
            {
                "name": "String",
                "type": "str",
                "required": True,
                "value": "default",
            },
            {"name": "Bool", "type": "bool", "required": True, "value": True},
            {"name": "Float", "type": "float", "required": True, "value": 1.0},
        ],
        "output": [
            {"name": "Test", "fields": [{"name": "Asset", "type": "Asset"}]}
        ],
        "tags": ["tag1", "tag2", "tag3"],
        "endpoints": [{"name": "proxy", "port": 1080}],
    }
)


@dataclass
class SubprocessOutput:
    stderr: str
    stdout: str
    returncode: int


class MockLogsStreamer:
    def start(self):
        return None


def test_create_component():
    manager = ComponentManager()
    path = "."
    abs_path = os.path.abspath(path)
    with patch(
        "splight_cli.component.component.open", mock_open()
    ) as mocked_file:
        manager.create(
            name="new_component", version="1.1.1", component_path=path
        )
        mocked_file.assert_has_calls(
            [
                call(os.path.join(abs_path, file_name), "w+")
                for file_name in COMPONENT_FILES
            ],
            any_order=True,
        )
