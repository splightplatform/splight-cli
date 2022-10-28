from private_splight_lib.settings import setup
from splight_lib import logging
from splight_models import HubComponentVersion
from pydantic import BaseModel, BaseSettings
import argparse
import docker
from docker.errors import BuildError, APIError
import os

logger = logging.getLogger(__name__)


class Context(BaseSettings):
    WORKSPACE: str
    REGISTRY: str


class BuildSpec(BaseModel):
    name: str
    type: str
    version: str
    access_id: str
    secret_key: str
    cli_version: str
    api_host: str


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

    context = Context()

    hub_client = get_hub_client(build_spec)

    component_name = build_spec.name
    component_version = build_spec.version
    component_type = build_spec.type

    component = hub_client.mine.get(
        HubComponentVersion,
        name=component_name,
        version=component_version,
        type=component_type.lower()
    )[0]

    # component.build_status = "building"
    # hub_client.mine.update(HubComponentVersion, id=component.id, data=component.dict())

    try:
        build_tag = component_name.lower()
        tag = f"{context.REGISTRY}/splight-components:{component_name}-{context.WORKSPACE}-{component_version}"
        tag = tag.lower()
        docker_client = docker.from_env()
        logger.info("Building image")
        runner_image = f"{context.REGISTRY}/splight-runner:{context.WORKSPACE}-{build_spec.cli_version}"
        print('DEBUG')
        print(args.build_spec[0])
        print(tag)
        print(runner_image)
        print('CMD')
        os.system(f'docker image rm {runner_image}')
        os.system('docker login -u AWS -p $(aws ecr get-login-password --region us-east-1) 609067598877.dkr.ecr.us-east-1.amazonaws.com')
        print(f"docker build -t {tag} --build-arg RUNNER_IMAGE={runner_image} --build-arg CONFIGURE_SPEC='{args.build_spec[0]}' .")
        os.system(f"docker build -t {tag} --build-arg RUNNER_IMAGE={runner_image} --build-arg CONFIGURE_SPEC='{args.build_spec[0]}' .")
        # os.system(f'docker tag {build_tag} {tag}')
        os.system(f'docker push {tag}')
        # docker_client.images.build(
        #     path=".",
        #     buildargs={
        #         "RUNNER_IMAGE": f"{context.REGISTRY}/splight-runner:{context.WORKSPACE}-{build_spec.cli_version}",
        #         "CONFIGURE_SPEC": args.build_spec[0],
        #     },
        #     tag=tag
        # )

        # logger.info("Pushing image")
        # docker_client.images.push(context.REGISTRY, tag)

    except (APIError, BuildError) as e:
        logger.exception(e)
        # component.build_status = "failed"
        # hub_client.mine.update(HubComponentVersion, id=component.id, data=component.dict())
        exit(1)

    # component.build_status = "success"
    # hub_client.mine.update(HubComponentVersion, id=component.id, data=component.dict())
