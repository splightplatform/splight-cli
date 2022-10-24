from private_splight_lib.settings import setup
from splight_lib import logging
from splight_models import HubComponentVersion
from pydantic import BaseModel
import argparse
import docker
from docker.errors import BuildError, APIError

logger = logging.getLogger(__name__)


class BuildSpec(BaseModel):
    name: str
    type: str
    version: str
    access_id: str
    secret_key: str
    workspace: str
    registry: str


def get_hub_client(build_spec: BuildSpec):
    HubClient = setup.HUB_CLIENT
    headers = {
        "Authorization": f"Splight {build_spec.access_id} {build_spec.secret_key}"
    }
    return HubClient(headers=headers)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='Builds a hub component image.'
    )
    parser.add_argument('-b',
                        '--build-spec',
                        type=str,
                        nargs=1,
                        help='Build Spec',
                        required=True)
    args = parser.parse_args()
    build_spec = BuildSpec.parse_raw(args.build_spec[0])
    hub_client = get_hub_client(build_spec)

    component_name = build_spec.name
    component_version = build_spec.version.split("-")[1]
    component_type = build_spec.type

    component = hub_client.mine.get(HubComponentVersion, name=component_name, version=component_version, type=component_type.lower())[0]
    component.build_status = "building"
    hub_client.mine.update(HubComponentVersion, id=component.id, data=component.dict())

    try:
        tag = f"splight-runner:{build_spec.workspace}-{component_name}-{component_version}"
        docker_client = docker.from_env()
        logging.info("Building image")
        docker_client.images.build(
            path=".",
            buildargs={
                "BASE_IMAGE": f"{build_spec.registry}/splight-runner:{build_spec.workspace}",
                "BUILD_SPEC": args.build_spec[0],
            },
            tag=tag
        )

        logging.info("Pushing image")
        docker_client.images.push(build_spec.registry, tag)

    except (APIError, BuildError) as e:
        logger.exception(e)
        component.build_status = "failed"
        hub_client.mine.update(HubComponentVersion, id=component.id, data=component.dict())
        exit(1)

    component.build_status = "success"
    hub_client.mine.update(HubComponentVersion, id=component.id, data=component.dict())
