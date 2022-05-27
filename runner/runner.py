import argparse
import os
import json
import subprocess
SPLIGHT_PATH = os.path.join(os.path.expanduser("~"), '.splight')
CONFIG_FILE = os.path.join(SPLIGHT_PATH, 'hub.conf')

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

    if not os.path.exists(SPLIGHT_PATH):
        os.makedirs(SPLIGHT_PATH)
        
    with open(CONFIG_FILE, 'w+') as hub_config:
        hub_config.write(f"SPLIGHT_ACCESS_ID={os.getenv('BOT_HUB_ACCESS_ID')}")
        hub_config.write(f"\nSPLIGHT_SECRET_KEY={os.getenv('BOT_HUB_SECRET_KEY')}")
        hub_config.write(f"\nSPLIGHT_HUB_API_HOST={os.getenv('SPLIGHT_HUB_HOST')}")
    
    subprocess.run(["splighthub", "pull", hub_type, hub_name, hub_version], check=True)
    subprocess.run(["splighthub", "install-requirements", hub_type, hub_descriptor], check=True)
    subprocess.run(["splighthub", "run", hub_type, hub_descriptor, json.dumps(run_spec)], check=True)
