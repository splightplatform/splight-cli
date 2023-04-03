from packaging import version
import subprocess
import sys

def get_version_from_line(line):
    ver_str = line.split(" ")[-1][1:-1]
    return version.parse(ver_str)


if __name__ == "__main__":
    branch_name = sys.argv[1]
    cmd = ["git", "diff", f"master..{branch_name}", "--", "cli/version.py"]
    output = subprocess.check_output(cmd)
    output_lines = output.decode().split("\n")
    print(output_lines)

    try:
        old_version_line = output_lines[-3]
        new_version_line = output_lines[-2]
    except:
        print("bn", branch_name, "argv", sys.argv, "l", output_lines)

    old_version = get_version_from_line(old_version_line)
    new_version = get_version_from_line(new_version_line)

    if new_version <= old_version:
        raise Exception(
            f"local version {project_version} is not greater than"
            f"uploaded version {public_project_version}"
        )
