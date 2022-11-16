import os
from pathlib import Path
from splight_models import ComponentType

from cli.settings import SplightCLISettings


SPLIGHT_PATH = os.path.join(os.path.expanduser("~"), '.splight')
BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_FOLDER = os.path.join(BASE_DIR, "cli", "component", "templates")

COMPRESSION_TYPE = "7z"
DEFAULT_NAMESPACE = 'NO_NAMESPACE'
DEFAULT_COMPONENT_ID = "DEMO"
DEFAULT_WORKSPACE_NAME = 'default'
DEFAULT_WORKSPACE = SplightCLISettings().dict()
DEFAULT_WORKSPACES = {
    DEFAULT_WORKSPACE_NAME: DEFAULT_WORKSPACE
}

CONFIG_FILE = os.path.join(SPLIGHT_PATH, 'config')
COMPONENT_FILE = "__init__.py"
SPEC_FILE = "spec.json"
INIT_FILE = "Initialization"
README_FILE = "README"
PICTURE_FILE = "picture.jpg"
VARS_FILE = "vars.svars"

REQUIRED_FILES = [COMPONENT_FILE, SPEC_FILE, INIT_FILE, README_FILE, PICTURE_FILE]

MAIN_CLASS_NAME = "Main"

VALID_TYPES = [component.value for component in ComponentType]
VALID_PARAMETER_VALUES = {
    "int": int,
    "bool": bool,
    "str": str,
    "float": float,
    "Date": None,
    "file": None,  # UUID
    "Asset": None,  # UUID,
    "Algorithm": None,  # UUID,
    "Attribute": None,  # UUID,
    "Connector": None,  # UUID,
    "Graph": None,  # UUID,
    "Network": None,  # UUID,
    "Rule": None,  # UUID,
    "Query": None, # UUID,
}

VALID_DEPENDS_ON = [
    ("Asset", "Graph"),
    ("Attribute", "Asset"),
]
