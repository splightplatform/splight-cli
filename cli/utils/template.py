import os
from jinja2 import Template
from ..settings import TEMPLATES_FOLDER, PICTURE_FILE, SPLIGHT_HUB_API_HOST
from .api_requests import api_get
from tempfile import NamedTemporaryFile
from .handler import UserHandler


class MissingTemplate(Exception):
    pass


def get_template(name) -> Template:
    template_path = os.path.join(TEMPLATES_FOLDER, name)
    if not os.path.exists(template_path):
        raise MissingTemplate(f"Unable to find template {template_path}")
    with open(template_path, "r+") as f:
        content = f.read()
    return Template(content)
