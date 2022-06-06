import os
from pathlib import Path
from uuid import UUID

TEMPLATES_FOLDER = os.path.join(Path(__file__).resolve().parent, "templates")

SPLIGHT_HUB_API_HOST = os.getenv("SPLIGHT_HUB_HOST", "https://hub.splight-ae.com/")
COMPRESSION_TYPE = "7z"

COMPONENT_FILE = "__init__.py"
SPEC_FILE = "spec.json"
INIT_FILE = "Initialization"
README_FILE = "README"
REQUIRED_FILES = [COMPONENT_FILE, SPEC_FILE, INIT_FILE, README_FILE]
MAIN_CLASS_NAME = "Main"
VALID_TYPES = ["algorithm", "connector", "network"]
VALID_SIZE_VALUES = ["S", "M", "L", "XL", "XXL"]
VALID_PARAMETER_VALUES = {
    "int": int,
    "bool": bool,
    "str": str,
    "float": float,
    "file": None, #UUID
    "Asset": None, #UUID,
    "Attribute": None, #UUID,
    "Network": None, #UUID,
    "Algorithm": None, #UUID,
    "Connector": None, #UUID,
    "Rule": None, #UUID,
}