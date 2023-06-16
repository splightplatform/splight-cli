import os
from dataclasses import dataclass
from unittest.mock import call, mock_open, patch

import pytest
from cli.component.component import ComponentManager
from cli.component.exceptions import (
    ComponentExecutionError,
    InvalidSplightCLIVersion,
)
from splight_lib.component.spec import Spec

COMPONENT_FILES = [
    "Initialization",
    "README.md",
    "spec.json",
    ".splightignore",
    "tests.py",
]

SPEC = Spec.parse_obj(
    {
        "name": "TestComponent",
        "version": "0.1.0",
        "splight_cli_version": "1.1.1",
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
        "commands": [
            {"name": "Hello", "fields": [{"name": "message", "type": "str"}]}
        ],
        "tags": ["tag1", "tag2", "tag3"],
        "bindings": [],
        "endpoints": [{"name": "proxy", "port": 1080}],
    }
)


@dataclass
class SubprocessOutput:
    stderr: str
    stdout: str
    returncode: int


def test_create_component():
    manager = ComponentManager()
    path = "."
    abs_path = os.path.abspath(path)
    with patch("cli.component.component.open", mock_open()) as mocked_file:
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


@patch(
    "cli.component.component.subprocess.run",
    return_value=SubprocessOutput(stderr="", stdout="", returncode=0),
)
@patch.object(ComponentManager, "_validate_cli_version", return_value=None)
@patch.object(Spec, "from_file", return_value=SPEC)
def test_run_component(mock_spec, mock_cli_version, mock_run):
    manager = ComponentManager()
    manager.run(path=".", component_id="1234")


@patch(
    "cli.component.component.subprocess.run",
    return_value=SubprocessOutput(stderr="", stdout="", returncode=0),
)
@patch.object(Spec, "from_file", return_value=SPEC)
def test_run_component_invalid_cli_version(mock_spec, mock_run):
    manager = ComponentManager()
    with pytest.raises(InvalidSplightCLIVersion):
        manager.run(path=".", component_id="1234")


@patch(
    "cli.component.component.subprocess.run",
    return_value=SubprocessOutput(stderr="", stdout="", returncode=1),
)
@patch.object(ComponentManager, "_validate_cli_version", return_value=None)
@patch.object(Spec, "from_file", return_value=SPEC)
def test_run_component_with_error(mock_spec, mock_cli_version, mock_run):
    manager = ComponentManager()
    with pytest.raises(ComponentExecutionError):
        manager.run(path=".", component_id="1234")
