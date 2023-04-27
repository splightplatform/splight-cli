import json
import sys
from packaging.version import parse
import requests


class VersionError(Exception):
    """Raised when the version is not greater than the one on pypi"""
    pass


def get_pypi_version(project_name: str):
    url = f"https://pypi.org/pypi/{project_name}/json"
    response = requests.get(url)
    response.raise_for_status()
    version = json.loads(response.content)["info"]["version"]
    return parse(version)

if __name__ == "__main__":
    """Compares versions between the local repository
    and the package on pypi.

    Args:
        version_file (arg 1) (str): path to the version file
            must be a one liner containing the version
            number between double quotes.
        project_name (arg 2) (str): name of the project on pypi
    Raises:
        VersionError: if the local version is not greater than
            the one on pypi
    """
    version_file = sys.argv[1]
    project_name = sys.argv[2]

    with open(version_file, "r") as f:
        string_version = f.readline().split('"')[1]

    project_version = parse(string_version)
    public_project_version = get_pypi_version(project_name)

    if project_version <= public_project_version:
        raise VersionError(
            f"Feature version {project_version} is not greater than "
            f"uploaded version {public_project_version}"
        )
