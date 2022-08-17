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
    # TODO remove this overparsing
    hub_type = run_spec["type"].lower()
    hub_descriptor = run_spec["version"]
    hub_name, hub_version = hub_descriptor.split("-")
    access_id = run_spec.get("access_id", None)
    secret_key = run_spec.get("secret_key", None)

    json_configuration = {
        "SPLIGHT_ACCESS_ID": access_id,
        "SPLIGHT_SECRET_KEY": secret_key,
        "SPLIGHT_PLATFORM_API_HOST": os.getenv('SPLIGHT_PLATFORM_API_HOST'),
        # TODO REMOVE THIS
        "SPLIGHT_HUB_API_HOST": os.getenv('SPLIGHT_HUB_HOST'),
    }
    subprocess.run(["splightcli", "configure", "--from-json", json.dumps(json_configuration)], check=True)
    subprocess.run(["splightcli", "component", "pull", hub_type, hub_name, hub_version], check=True)
    subprocess.run(["splightcli", "component", "install-requirements", hub_type, hub_descriptor], check=True)
    subprocess.run(["splightcli", "component", "run", hub_type, hub_descriptor, json.dumps(run_spec)], check=True)
