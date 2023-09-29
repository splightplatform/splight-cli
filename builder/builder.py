import base64
import logging
from functools import cached_property

import boto3
import docker
import typer
from constants import BuildStatus
from docker.errors import APIError, BuildError
from pydantic import BaseSettings
from schemas import BuildSpec, HubComponent

app = typer.Typer(name="Splight Component Builder")
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()


class Context(BaseSettings):
    SPLIGHT_API_HOST: str
    WORKSPACE: str
    REGISTRY: str
    REPOSITORY_NAME: str = "splight-components"


class Builder:
    _component_capacity = [
        ("small", 0.5),
        ("medium", 4),
        ("large", 8),
        ("very_large", 16),
    ]

    _docker_client = None

    def __init__(self, build_spec: BuildSpec):
        self.build_spec = build_spec
        self.context = Context()
        self.hub_component = HubComponent(
            id=self.build_spec.id,
            name=self.build_spec.name,
            version=self.build_spec.version,
            splight_cli_version=self.build_spec.cli_version,
            build_status=BuildStatus.UNKNOWN,
            min_component_capacity="small",
        )

    def build_and_push_component(self):
        logger.info("Building and pushing component")
        try:
            self.hub_component.build_status = BuildStatus.BUILDING
            self.hub_component.save()
            self._build_component()
            self._push_component()
            self._update_min_component_capacity()
            self.hub_component.build_status = BuildStatus.SUCCESS
            self.hub_component.save()
        except Exception as exc:
            logger.exception(exc)
            logger.error("Build failed: ", exc)
            self.hub_component.build_status = BuildStatus.FAILED
            self.hub_component.save()

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
        return f"{self.registry}/splight-admin:0.1.0rc0"
        # return f"{self.registry}/splight-runner:{self.build_spec.cli_version}"

    @property
    def tag(self):
        name = self.build_spec.name
        version = self.build_spec.version
        return f"{self.repository}:{name}-{self.workspace}-{version}".lower()

    @cached_property
    def aws_password(self):
        logger.info("Getting AWS password")
        ecr_client = boto3.client("ecr", region_name="us-east-1")
        token = ecr_client.get_authorization_token()
        return (
            base64.b64decode(
                token["authorizationData"][0]["authorizationToken"]
            )
            .decode()
            .split(":")[1]
        )

    @property
    def docker_client(self):
        if self._docker_client is None:
            logger.info("Creating docker client")
            docker_client = docker.from_env()
            result = docker_client.login(
                username="AWS",
                password=self.aws_password,
                registry=self.registry,
            )
            logger.info(f"Login result: {result}")
            self._docker_client = docker_client
        return self._docker_client

    def _build_component(self):
        logger.info("Building component")
        try:
            # TODO: add dockerfile to use
            _, build_logs = self.docker_client.images.build(
                path=".",
                tag=self.tag,
                buildargs={
                    "RUNNER_IMAGE": self.runner_image,
                    "SPLIGHT_CLI_VERSION": self.build_spec.cli_version,
                    "CONFIGURE_SPEC": self.build_spec.json(),
                },
                network_mode="host",
                pull=True,
            )
        except BuildError as exc:
            logger.exception(exc)
            logger.error(f"Error building component: {exc}")
            raise exc
        else:
            self._show_build_logs(build_logs)

    def _show_build_logs(self, build_logs):
        for log in build_logs:
            logger.debug(log)

    def _push_component(self):
        logger.info("Pushing component image")
        try:
            result = self.docker_client.images.push(self.tag)
            logger.info(f"Pushed result: {result}")
        except APIError as e:
            logger.error(f"Error pushing component: {e}")
            raise e

    def _update_min_component_capacity(self):
        logger.info("Saving image size")
        image = self.docker_client.images.get(self.tag)
        # get image size in GB
        image_size = float(image.attrs["Size"] / 10**9)
        self.hub_component.min_component_capacity = (
            self._get_min_component_capacity(image_size)
        )

    def _get_min_component_capacity(self, image_size: float) -> str:
        for size, cap in self._component_capacity:
            if image_size <= cap:
                return size
        return "very_large"

    def _save_component(self):
        logger.info("Saving component")
        try:
            self.component_manager.update(component=self.hub_component)
        except Exception as e:
            logger.error(f"Error saving component: {e}")


@app.command()
def main(
    build_spec_base64: str = typer.Option(
        ...,
        "-b",
        "--build-spec",
        help="build spec as base64",
    )
):
    build_spec_str = base64.b64decode(build_spec_base64).decode("utf-8")
    build_spec = BuildSpec.parse_raw(build_spec_str)
    logger.debug(f"Build spec: {build_spec.json()}")

    builder = Builder(build_spec)
    builder.build_and_push_component()


if __name__ == "__main__":
    app()
