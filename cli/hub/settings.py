import os
from pathlib import Path

VALID_COMPONENTS = [
    "algorithm",
    "io",
    "network"
]

IO_TYPES = [
    "client",
    "server"
]

TEMPLATES_FOLDER = os.path.join(Path(__file__).resolve().parent, "templates")