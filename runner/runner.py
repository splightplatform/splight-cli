import argparse
from asyncio.log import logger
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
    access_id = run_spec.get("access_id", None)
    secret_key = run_spec.get("secret_key", None)
    api_host = run_spec.get("api_host", None)
    component_id = run_spec.get("component_id", None)

    json_configuration = {
        "SPLIGHT_ACCESS_ID": access_id,
        "SPLIGHT_SECRET_KEY": secret_key,
        "SPLIGHT_PLATFORM_API_HOST": api_host,
        "COMPONENT_ID": component_id,
    }
    subprocess.run(["splightcli", "configure", "--from-json", json.dumps(json_configuration)], check=True)
    subprocess.run(["splightcli", "component", "run", hub_type, hub_descriptor, "--run-spec", json.dumps(run_spec)], check=True)
