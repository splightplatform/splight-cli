from private_splight_lib.settings import setup
from splight_models import HubComponentVersion
from splight_models.constants import BuildStatus
from splight_lib import logging
from pydantic import BaseModel, BaseSettings
from functools import cached_property
from docker.errors import BuildError, APIError
import docker
import argparse
import base64
import boto3

logger = logging.getLogger(__name__)


class Context(BaseSettings):
    WORKSPACE: str
    REGISTRY: str
    REPOSITORY_NAME: str = "splight-components"


class BuildSpec(BaseModel):
    name: str
    type: str
    version: str
    access_id: str
    secret_key: str
    cli_version: str
    api_host: str


class Builder:
    _docker_client = None

    def __init__(self, build_spec: BuildSpec):
        self.build_spec = build_spec
        self.context = Context()

    def build_and_push_component(self):
        logger.info("Building and pushing component")
        try:
            self._update_component_build_status(BuildStatus.BUILDING)
            self._build_component()
            self._push_component()
            self._update_component_build_status(BuildStatus.SUCCESS)
        except Exception as e:
            self._update_component_build_status(BuildStatus.FAILED)

    def delete_credentials(self):
        logger.info("Deleting credentials")
        AuthClient = setup.AUTH_CLIENT
        auth_client = AuthClient(headers=self.credentials)
        auth_client.deployment.destroy(build_spec.access_id)

    @property
    def registry(self):
        return self.context.REGISTRY

    @property
    def workspace(self):
        return self.context.WORKSPACE

    @property
    def repository_name(self):
        return self.context.REPOSITORY_NAME

    @property
    def repository(self):
        return f"{self.registry}/{self.repository_name}"

    @property
    def credentials(self):
        headers = {
            "Authorization": f"Splight {build_spec.access_id} {build_spec.secret_key}"
        }
        return headers

    @property
    def runner_image(self):
        return f"{self.registry}/splight-runner:{self.workspace}-{self.build_spec.cli_version}"

    @property
    def tag(self):
        name = self.build_spec.name
        version = self.build_spec.version
        return f"{self.repository}:{name}-{self.workspace}-{version}".lower()

    @cached_property
    def aws_password(self):
        logger.info("Getting AWS password")
        ecr_client = boto3.client('ecr', region_name='us-east-1')
        token = ecr_client.get_authorization_token()
        return base64.b64decode(token["authorizationData"][0]["authorizationToken"]).decode().split(":")[1]

    @cached_property
    def hub_client(self):
        logger.info("Creating hub client")
        HubClient = setup.HUB_CLIENT
        return HubClient(headers=self.credentials)

    @property
    def docker_client(self):
        if self._docker_client is None:
            logger.info("Creating docker client")
            docker_client = docker.from_env()
            result = docker_client.login(
                username="AWS",
                password=self.aws_password,
                registry=self.registry
            )
            logger.info(f"Login result: {result}")
            self._docker_client = docker_client
        return self._docker_client

    @cached_property
    def hub_component(self):
        logger.info("Getting hub component")
        return self.hub_client.mine.get(
            HubComponentVersion,
            type=self.build_spec.type,
            name=self.build_spec.name,
            version=self.build_spec.version
        )[0]

    def _build_component(self):
        logger.info("Building component")
        try:
            self.docker_client.images.build(
                path=".",
                tag=self.tag,
                buildargs={
                    "RUNNER_IMAGE": self.runner_image,
                    "CONFIGURE_SPEC": self.build_spec.json()
                }
            )
        except BuildError as e:
            logger.error(f"Error building component: {e}")
            raise e

    def _push_component(self):
        logger.info("Pushing component")
        try:
            result = self.docker_client.images.push(self.tag)
            logger.info(f"Push result: {result}")
        except APIError as e:
            logger.error(f"Error pushing component: {e}")
            raise e

    def _update_component_build_status(self, build_status: BuildStatus):
        # TODO: Update this to use a webhook
        logger.info(f"Updating component build status to {build_status}")
        self.hub_component.build_status = build_status
        try:
            self.hub_client.mine.update(
                HubComponentVersion,
                id=self.hub_component.id,
                data=self.hub_component.dict()
            )
        except Exception as e:
            logger.error(f"Error updating component build status: {e}")


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

    builder = Builder(build_spec)
    builder.build_and_push_component()
    builder.delete_credentials()