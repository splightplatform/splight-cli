import json
import subprocess
from asyncio.log import logging
from typing import Dict

import typer
from pydantic import BaseSettings, validator

app = typer.Typer(name="Splight Component Runner")


class RunnerConfig(BaseSettings):
    NAMESPACE: str
    SPLIGHT_ACCESS_ID: str
    SPLIGHT_SECRET_KEY: str
    SPLIGHT_PLATFORM_API_HOST: str
    COMPONENT_ID: str

    @validator("SPLIGHT_PLATFORM_API_HOST")
    def remove_trailing_slash(cls, value):
        return value.rstrip("/")


class SplightComponentRunner:

    _BASE_CMD = "splightcli"

    def __init__(
        self, component_name: str, component_version: str, component_type: str
    ):
        self._name = component_name
        self._version = component_version
        self._type = component_type

        logging.basicConfig(
            level=logging.INFO, format="%(asctime)s - %(name)s - %(message)s"
        )
        self._logger = logging.getLogger("Splight Runner")

    def configure(self, config: str):
        try:
            self._logger.info("Configuring splightcli")
            subprocess.run(
                [self._BASE_CMD, "configure", "--from-json", config],
                check=True,
            )
            self._logger.info(f"Runner configured with {config}")
        except subprocess.CalledProcessError as exc:
            self._logger.error(f"Error configuring component: {exc}")
            self._logger.error(f"Stdout: {exc.stdout}")
            self._logger.error(f"Stderr: {exc.stderr}")
            exit(1)

    def run(self, component_spec: Dict):
        try:
            self._run_component(component_spec)
        except subprocess.CalledProcessError as exc:
            self._logger.error(f"Error running component: {exc}")
            self._logger.error(f"Stdout: {exc.stdout}")
            self._logger.error(f"Stderr: {exc.stderr}")
            exit(1)

    def _run_component(self, component_spec: Dict):
        self._logger.info("Running component")
        subprocess.run(
            [
                self._BASE_CMD,
                "component",
                "run",
                self._type,
                f"{self._name}-{self._version}",
                "--run-spec",
                json.dumps(component_spec),
            ],
            check=True,
        )


@app.command()
def main(
    run_spec_str: str = typer.Option(
        ..., "--run-spec", "-r", help="Component spec as string"
    )
):
    config = RunnerConfig()

    run_spec = json.loads(run_spec_str)

    hub_type = run_spec["type"].lower()
    hub_descriptor = run_spec["version"]
    hub_name, hub_version = hub_descriptor.split("-")

    runner = SplightComponentRunner(
        component_name=hub_name,
        component_version=hub_version,
        component_type=hub_type,
    )
    runner.configure(config.json())
    runner.run(run_spec)


if __name__ == "__main__":
    app()
