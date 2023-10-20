import base64
import logging
from functools import cached_property

import boto3
import docker
import typer
from constants import NEW_RUNNER_CLI_VERSION
from docker.errors import APIError, BuildError
from packaging import version
from pydantic_settings import BaseSettings
from settings import aws_config
from splight_lib_internal.constants.builder import BuildStatus
from splight_lib_internal.schemas.builder import BuildSpec, HubComponent

app = typer.Typer(name="Splight Component Builder")
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()


class Context(BaseSettings):
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
        cli_version = version.parse(self.build_spec.cli_version).release
        if cli_version < version.parse(NEW_RUNNER_CLI_VERSION).release:
            return (
                f"{self.registry}/splight-runner:{self.build_spec.cli_version}"
            )
        else:
            return f"{self.registry}/splight-admin:latest"

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
                    "CONFIGURE_SPEC": self.build_spec.model_dump_json(),
                    "AWS_ACCESS_KEY_ID": aws_config.AWS_ACCESS_KEY_ID,
                    "AWS_SECRET_ACCESS_KEY": aws_config.AWS_SECRET_ACCESS_KEY,
                    "S3_BUCKET_NAME": aws_config.S3_BUCKET_NAME,
                },
                network_mode="host",
                pull=True,
            )
        except BuildError as exc:
            error_message = exc.build_log
            for log_entry in error_message:
                for _, message in log_entry.items():
                    logger.debug(message)

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


@app.command()
def main(
    build_spec_str: str = typer.Option(
        ...,
        "-b",
        "--build-spec",
        help="build spec as string",
    )
):
    build_spec_str = build_spec_str.replace("=", ":")
    build_spec = BuildSpec.model_validate_json(build_spec_str)
    logger.debug(f"Build spec: {build_spec.model_dump_json()}")

    builder = Builder(build_spec)
    builder.build_and_push_component()


if __name__ == "__main__":
    app()
