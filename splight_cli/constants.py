import os
from pathlib import Path

from pydantic import AnyUrl
from rich.style import Style

from splight_cli.settings import SplightCLISettings

error_style = Style(color="red", bold=True)
success_style = Style(color="green")
warning_style = Style(color="yellow")

SPLIGHT_PATH = os.path.join(os.path.expanduser("~"), ".splight")
BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_FOLDER = os.path.join(
    BASE_DIR, "splight_cli", "component", "templates"
)

COMPRESSION_TYPE = "7z"
DEFAULT_NAMESPACE = "NO_NAMESPACE"
DEFAULT_COMPONENT_ID = "DEMO"
DEFAULT_WORKSPACE_NAME = "default"
DEFAULT_WORKSPACE = SplightCLISettings().model_dump()
DEFAULT_WORKSPACES = {DEFAULT_WORKSPACE_NAME: DEFAULT_WORKSPACE}

CONFIG_FILE = os.path.join(SPLIGHT_PATH, "config")
PYTHON_COMPONENT_FILE = "main.py"
SPEC_FILE = "spec.json"
INIT_FILE = "Initialization"
README_FILE = "README.md"
README_FILE_2 = "README"
MAIN_CLASS_NAME = "Main"
SPLIGHT_IGNORE = ".splightignore"
PYTHON_TESTS_FILE = "tests.py"

PYTHON_CMD = "python"
PYTHON_TEST_CMD = "pytest"

REQUIRED_DATALAKE_COLUMNS = {
    "timestamp",
    "asset",
    "attribute",
    "value",
    "output_format",
}

VALID_PARAMETER_VALUES = {
    "int": int,
    "bool": bool,
    "str": str,
    "float": float,
    "url": AnyUrl,
    "datetime": None,
    "file": None,  # UUID
    "File": None,  # UUID
    "Asset": None,  # UUID,
    "Attribute": None,  # UUID,
    "Component": None,  # UUID,
    "Graph": None,  # UUID,
    "Query": None,  # UUID,
    "Mapping": None,  # UUID
}

VALID_DEPENDS_ON = [
    ("Asset", "Graph"),
    ("Attribute", "Asset"),
]
