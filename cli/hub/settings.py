import os
from pathlib import Path
from uuid import UUID

TEMPLATES_FOLDER = os.path.join(Path(__file__).resolve().parent, "templates")
API_URL = os.getenv("API_URL", "a01b003a9c5f84df28175172162e0eba-1503054634.us-east-1.elb.amazonaws.com")
COMPRESSION_TYPE = "7z"

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
    "Asset": None, #UUID,
    "Attribute": None, #UUID,
    "Network": None, #UUID,
    "Algorithm": None, #UUID,
    "Connector": None, #UUID,
    "Rule": None, #UUID,
}