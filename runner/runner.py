import argparse
import os
import json
import subprocess

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Executes a hub component.'
    )
    parser.add_argument('-r',
                        '--run-spec',
                        type=str,
                        nargs=1,
                        help='Run Spec',
                        required=True)
                        
    args = parser.parse_args()
    run_spec = json.loads(args.run_spec[0])
    hub_type = run_spec["type"].lower()
    hub_descriptor = run_spec["version"]
    hub_name, hub_version = hub_descriptor.split("-")

    json_configuration = {
        "SPLIGHT_PLATFORM_API_HOST": os.getenv('SPLIGHT_PLATFORM_API_HOST'),
        # TODO use particular keys for the respective org
        "SPLIGHT_ACCESS_ID": os.getenv('BOT_HUB_ACCESS_ID'),
        "SPLIGHT_SECRET_KEY": os.getenv('BOT_HUB_SECRET_KEY'),
        # TODO REMOVE THIS
        "SPLIGHT_HUB_API_HOST": os.getenv('SPLIGHT_HUB_HOST'),
    }
    subprocess.run(["splightcli", "configure", "--from-json", json.dumps(json_configuration)], check=True)
    subprocess.run(["splightcli", "component", "pull", hub_type, hub_name, hub_version], check=True)
    subprocess.run(["splightcli", "component", "install-requirements", hub_type, hub_descriptor], check=True)
    subprocess.run(["splightcli", "component", "run", hub_type, hub_descriptor, json.dumps(run_spec)], check=True)
