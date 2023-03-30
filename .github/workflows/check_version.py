import json
import os
from packaging import version
import requests
import sys


PROJECT_NAME = "splight-cli"
VERSION_PATH = "cli/version.py"


def get_public_version(project_name: str):
    response = requests.get(f"https://pypi.org/pypi/{project_name}/json")
    response.raise_for_status()
    return version.parse(json.loads(response.content)["info"]["version"])


if __name__ == "__main__":
    with open(VERSION_PATH, "r") as f:
        string_version = f.readline().split('"')[1]

    project_version = version.parse(string_version)
    public_project_version = get_public_version(PROJECT_NAME)

    if project_version < public_project_version:
        raise Exception(
            f"local version {project_version} is not greater than"
            f"uploaded version {public_project_version}"
        )