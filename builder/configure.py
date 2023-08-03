import argparse
import json
import subprocess
from asyncio.log import logger

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
    # TODO: search for a better approach
    renamed_version = hub_version.replace(".", "_")
    hub_descriptor = f"{hub_name}/{renamed_version}"
    access_id = configure_spec.get("access_id", None)
    secret_key = configure_spec.get("secret_key", None)
    api_host = configure_spec.get("api_host", None)
    grpc_host = configure_spec.get("grpc_host", None)

    json_configuration = {
        "SPLIGHT_ACCESS_ID": access_id,
        "SPLIGHT_SECRET_KEY": secret_key,
        "SPLIGHT_PLATFORM_API_HOST": api_host,
        "SPLIGHT_GRPC_HOST": grpc_host,
    }

    logger.info(
        f"Configure with {access_id} to configure {hub_name} {hub_version}."
        f" Remote set to {api_host}"
    )

    try:
        subprocess.run(
            [
                "splight",
                "configure",
                "--from-json",
                json.dumps(json_configuration),
            ],
            check=True,
        )
        subprocess.run(
            ["splight", "hub", "component", "pull", hub_name, hub_version],
            check=True,
        )
        subprocess.run(
            ["splight", "component", "install-requirements", hub_descriptor],
            check=True,
        )

    except subprocess.CalledProcessError as e:
        logger.error(f"Error configuring component: {e}")
        logger.error(f"Stdout: {e.stdout}")
        logger.error(f"Stderr: {e.stderr}")
        exit(1)
