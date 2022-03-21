import os
from pathlib import Path

VALID_COMPONENTS = [
    "algorithm",
    "io_client",
    "io_server",
    "io",
    "network"
]

TEMPLATES_FOLDER = os.path.join(Path(__file__).resolve().parent, "templates")