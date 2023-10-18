import argparse
import json

from install_requirements import HubComponentManager

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Executes a hub component.")
    parser.add_argument(
        "-c",
        "--configure-spec",
        type=str,
        nargs=1,
        help="Configure Spec",
        required=True,
    )

    args = parser.parse_args()
    configure_spec = json.loads(args.configure_spec[0])

    # TODO remove this overparsing
    hub_name = configure_spec["name"]
    hub_version = configure_spec["version"]
    hub_component_id = configure_spec["id"]

    manager = HubComponentManager(name=hub_name, version=hub_version)
    manager.download_component()
    manager.install_requirements()
    exit(0)
