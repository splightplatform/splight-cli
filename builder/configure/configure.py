import argparse
import json

from manager import HubComponentManager

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

    manager = HubComponentManager(spec=configure_spec)
    manager.download_component()
    manager.install_requirements()
