import os
from pathlib import Path
from uuid import UUID

TEMPLATES_FOLDER = os.path.join(Path(__file__).resolve().parent, "templates")
COMPONENT_FILE = "__init__.py"
SPEC_FILE = "spec.json"
INIT_FILE = "Initialization"
README_FILE = "README"
REQUIRED_FILES = [COMPONENT_FILE, SPEC_FILE, INIT_FILE, README_FILE]
MAIN_CLASS_NAME = "Main"
VALID_TYPES = ["algorithm", "connector", "network"]
VALID_PARAMETER_VALUES = {
    "int": int,
    "bool": bool,
    "str": str,
    "float": float,
    "file": str,
    "Asset": UUID,
    "Attribute": UUID,
    "Network": UUID,
    "Algorithm": UUID,
    "Connector": UUID,
    "Rule": UUID,
}