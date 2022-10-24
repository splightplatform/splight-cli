import argparse
from asyncio.log import logger
import json
import subprocess

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Executes a hub component.'
    )
    parser.add_argument('-c',
                        '--configure-spec',
                        type=str,
                        nargs=1,
                        help='Configure Spec',
                        required=True)

    args = parser.parse_args()
    configure_spec = json.loads(args.configure_spec[0])
    # TODO remove this overparsing
    hub_type = configure_spec["type"].lower()
    hub_descriptor = configure_spec["version"]
    hub_name, hub_version = hub_descriptor.split("-")
    access_id = configure_spec.get("access_id", None)
    secret_key = configure_spec.get("secret_key", None)
    api_host = configure_spec.get("api_host", None)

    json_configuration = {
        "SPLIGHT_ACCESS_ID": access_id,
        "SPLIGHT_SECRET_KEY": secret_key,
        "SPLIGHT_PLATFORM_API_HOST": api_host,
    }
    logger.info(f"Configure with {access_id} to configure {hub_type} {hub_name} {hub_version}. Remote set to {api_host}")
    subprocess.run(["splightcli", "configure", "--from-json", json.dumps(json_configuration)], check=True)
    subprocess.run(["splightcli", "component", "pull", hub_type, hub_name, hub_version], check=True)
    subprocess.run(["splightcli", "component", "install-requirements", hub_type, hub_descriptor], check=True)
