import logging

import typer
from splight_lib_internal.constants.builder import BuildStatus
from splight_lib_internal.schemas.builder import BuildSpec, HubComponent

app = typer.Typer(name="Splight Component Post Build")
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()


class PostBuild:
    def __init__(self, build_spec: BuildSpec):
        self.hub_component = HubComponent(
            id=build_spec.id,
            name=build_spec.name,
            version=build_spec.version,
            splight_cli_version=build_spec.cli_version,
            build_status=BuildStatus.UNKNOWN,
            min_component_capacity="small",
        )

    def set_success_status(self):
        logger.info("Set status to success")
        self.hub_component.build_status = BuildStatus.SUCCESS
        self.hub_component.save()


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

    builder = PostBuild(build_spec)
    builder.set_success_status()


if __name__ == "__main__":
    app()
