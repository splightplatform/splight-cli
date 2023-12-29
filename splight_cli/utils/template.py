import os

from jinja2 import Template

from splight_cli.constants import TEMPLATES_FOLDER


class MissingTemplate(Exception):
    pass


def get_template(name) -> Template:
    template_path = os.path.join(TEMPLATES_FOLDER, name)
    if not os.path.exists(template_path):
        raise MissingTemplate(f"Unable to find template {template_path}")
    with open(template_path, "r+") as f:
        content = f.read()
    return Template(content, autoescape=True)
