import os
import sys


def main():
    command = sys.argv[1:]
    main_file = command[0]
    if main_file.endswith(".py"):
        base_cmd = "python3"
    exec_path = sys.executable
    command.insert(0, base_cmd)
    print(command)
    os.execl(exec_path, *command)


if __name__ == "__main__":
    main()
