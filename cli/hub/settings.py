import os
from pathlib import Path

TEMPLATES_FOLDER = os.path.join(Path(__file__).resolve().parent, "templates")

API_URL = os.getenv("API_URL", "http://localhost:8000")