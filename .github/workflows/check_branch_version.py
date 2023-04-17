from packaging import version
import subprocess
import sys


if __name__ == "__main__":
    old_version_line = sys.argv[1]
    new_version_line = sys.argv[2]

    master_version = version.parse(old_version_line)
    project_version = version.parse(new_version_line)

    if project_version <= master_version:
        raise Exception(
            f"local version {project_version} is not greater than "
            f"master version {master_version}"
        )
