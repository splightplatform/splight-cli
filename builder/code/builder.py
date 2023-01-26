from private_splight_models import BuildSpec
from splight_models import HubComponent
from splight_models.constants import BuildStatus
from splight_lib import logging
from splight_lib.webhook import WebhookClient, WebhookEvent
from pydantic import BaseSettings
from functools import cached_property
from docker.errors import BuildError, APIError
import requests
import docker
import base64
import boto3
import typer


app = typer.Typer(name="Splight Component Builder")
logger = logging.getLogger(__name__)


class Context(BaseSettings):
    SPLIGHT_API_HOST: str
    WORKSPACE: str
    REGISTRY: str
    REPOSITORY_NAME: str = "splight-components"


class ComponentManager:
    def __init__(self, url):
        self.url = "/".join([url, "v2", "hub", "component", "webhook", ""])
        self.webhook_client = WebhookClient()

    def update(self, component: HubComponent):
        event = WebhookEvent(
            event_name="hubcomponent-update",
            object_type="HubComponent",
            data=component.dict()
        )
        payload, signature = self.webhook_client.construct_payload(event)
        headers = {'Splight-Signature': signature}
        request = requests.Request(
            "POST",
            self.url,
            data=payload,
            headers=headers
        )
        prepped = request.prepare()
        with requests.Session() as session:
            response = session.send(prepped)
        if response.status_code != 200:
            raise Exception(f"Error updating component: {response.status_code} - {response.content}")
        logger.info(f"{response.status_code} - {response.content}")


class Builder:
    _component_capacity = [
        ("small", 0.5),
        ("medium", 4),
        ("large", 8),
        ("very_large", 16)
    ]

    _docker_client = None

    def __init__(self, build_spec: BuildSpec):
        self.build_spec = build_spec
        self.context = Context()
        self.hub_component = HubComponent(
            name=self.build_spec.name,
            version=self.build_spec.version,
            splight_cli_version=self.build_spec.cli_version,
            build_status=BuildStatus.UNKNOWN
        )

    def build_and_push_component(self):
        logger.info("Building and pushing component")
        try:
            self._update_component_build_status(BuildStatus.BUILDING)
            self._build_component()
            self._push_component()
            self._update_min_component_capacity(save=False)
            self._update_component_build_status(BuildStatus.SUCCESS)
        except Exception as e:
            logger.info('Build failed: ', e)
            self._update_component_build_status(BuildStatus.FAILED)

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
    def component_manager(self):
        logger.info("Creating commponent manager")
        return ComponentManager(self.context.SPLIGHT_API_HOST)

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

    def _build_component(self):
        logger.info("Building component")
        try:
            self.docker_client.images.build(
                path=".",
                tag=self.tag,
                buildargs={
                    "RUNNER_IMAGE": self.runner_image,
                    "CONFIGURE_SPEC": self.build_spec.json()
                },
                network_mode="host",
                pull=True,
                vervose=True
            )
        except BuildError as e:
            logger.error(f"Error building component: {e}")
            raise e

    def _push_component(self):
        logger.info("Pushing component image")
        try:
            result = self.docker_client.images.push(self.tag)
            logger.info(f"Pushed result: {result}")
        except APIError as e:
            logger.error(f"Error pushing component: {e}")
            raise e

    def _update_component_build_status(self, build_status: BuildStatus, save: bool = True):
        logger.info(f"Updating component build status to {build_status}")
        self.hub_component.build_status = build_status
        if save:
            self._save_component()

    def _update_min_component_capacity(self, save: bool = True):
        logger.info("Saving image size")
        image = self.docker_client.images.get(self.tag)
        # get image size in GB
        image_size = float(image.attrs["Size"] / 10**9)
        self.hub_component.min_component_capacity = self._get_min_component_capacity(image_size)
        if save:
            self._save_component()

    def _get_min_component_capacity(self, image_size: float) -> str:
        for size, cap in self._component_capacity:
            if image_size <= cap:
                return size
        return "very_large"

    def _save_component(self):
        logger.info("Saving component")
        try:
            self.component_manager.update(
                component=self.hub_component
            )
        except Exception as e:
            logger.error(f"Error saving component: {e}")


@app.command()
def main(
    build_spec_str: str = typer.Option(..., "-b", "--build-spec", help="build spec as defined in the private lib")
):

    build_spec = BuildSpec.parse_raw(build_spec_str)

    builder = Builder(build_spec)
    builder.build_and_push_component()


if __name__ == "__main__":
    app()
