import argparse
import os
import json
import subprocess
SPLIGHT_PATH = os.path.join(os.path.expanduser("~"), '.splight')
CONFIG_FILE = os.path.join(SPLIGHT_PATH, 'hub.conf')

DATA = {
    'integration': {
        "access_id": "22ae05a3-84e9-4960-9b77-924d4073b462",
        "secret_key": "427b1c6eef0aff9515100d7d033159ee1fffbbc36d6b9739b14baf21e71d78ac",
        "api_host": "https://integrationhub.splight-ae.com",
        "platform_api_host": "https://integrationapi.splight-ae.com",
    },
    'production': {
        "access_id": "29208a92-8da4-4683-bde4-c5fbb47ff358",
        "secret_key": "1b45124c6515953889ad2bbc7e266b24dce13e6c8e1b3d8ba8d2e7621fbbd2b7",
        "api_host": "https://hub.splight-ae.com",
        "platform_api_host": "https://api.splight-ae.com",
    },
}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Executes a hub component.'
    )
    parser.add_argument('-w',
                        '--workspace',
                        type=str,
                        nargs=1,
                        help='workspace',
                        required=True)
                        
    args = parser.parse_args()
    workspace = args.workspace[0]

    if not os.path.exists(SPLIGHT_PATH):
        os.makedirs(SPLIGHT_PATH)
        
    with open(CONFIG_FILE, 'w+') as hub_config:
        hub_config.write(f"SPLIGHT_ACCESS_ID={DATA[workspace]['access_id']}")
        hub_config.write(f"\nSPLIGHT_SECRET_KEY={DATA[workspace]['secret_key']}")
        hub_config.write(f"\nSPLIGHT_HUB_API_HOST={DATA[workspace]['api_host']}\n")
        hub_config.write(f"\nSPLIGHT_PLATFORM_API_HOST={DATA[workspace]['platform_api_host']}\n")







