import os
from pathlib import Path
from functools import partial
from datetime import datetime
from uuid import UUID
from splight_models import *

TEMPLATES_FOLDER = os.path.join(Path(__file__).resolve().parent, "component", "templates")

SPLIGHT_HUB_API_HOST = os.getenv("SPLIGHT_HUB_HOST", "https://integrationhub.splight-ae.com/")
SPLIGHT_PLATFORM_API_HOST = os.getenv("SPLIGHT_API_HOST", "https://integrationapi.splight-ae.com/")
COMPRESSION_TYPE = "7z"

COMPONENT_FILE = "__init__.py"
SPEC_FILE = "spec.json"
INIT_FILE = "Initialization"
README_FILE = "README"
PICTURE_FILE = "picture.jpg"
REQUIRED_FILES = [COMPONENT_FILE, SPEC_FILE, INIT_FILE, README_FILE, PICTURE_FILE]
MAIN_CLASS_NAME = "Main"
VALID_TYPES = ["algorithm", "connector", "network"]
VALID_PARAMETER_VALUES = {
    "int": int,
    "bool": bool,
    "str": str,
    "float": float,
    "file": None,  # UUID
    "Asset": None,  # UUID,
    "Algorithm": None,  # UUID,
    "Attribute": None,  # UUID,
    "Connector": None,  # UUID,
    "Date": partial(datetime.strptime, format="%Y-%m-%dT%H:%M:%S%z"),  # datetime.datetime,
    "Graph": None,  # UUID,
    "Network": None,  # UUID,
    "Rule": None,  # UUID,
}

DATABASE_TYPES = {
    "Asset": Asset,
    "Algorithm": Algorithm,
    "Attribute": Attribute,
    "Connector": Connector,
    "Graph": Graph,
    "Network": Network,
    "Rule": MappingRule,
}

STORAGE_TYPES = {
    "file": StorageFile
}


VARS_FILE = os.getenv("SPLIGHT_HUB_VARS", "vars.svars")
BASE_DIR = Path(__file__).resolve().parent.parent
