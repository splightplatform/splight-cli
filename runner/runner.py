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
    SPLIGHT_ENCRYPTION_KEY: str

    class Config:
        secrets_dir: str = "/etc/config"

    @validator("SPLIGHT_PLATFORM_API_HOST")
    def remove_trailing_slash(cls, value):
        return value.rstrip("/")


class SplightComponentRunner:

    _BASE_CMD = "splightcli"

    def __init__(
        self, component_name: str, component_version: str
    ):
        self._name = component_name
        self._version = component_version

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
            self._logger.info("Running component")
            input_spec = component_spec['input']
            subprocess.run(
                [
                    self._BASE_CMD,
                    "component",
                    "run",
                    f"{self._name}/{self._version}",
                    "--input",
                    json.dumps(input_spec),
                ],
                check=True,
            )
        except subprocess.CalledProcessError as exc:
            self._logger.error(f"Error running component: {exc}")
            self._logger.error(f"Stdout: {exc.stdout}")
            self._logger.error(f"Stderr: {exc.stderr}")
            exit(1)


@app.command()
def main(
    run_spec_str: str = typer.Option(
        ..., "--run-spec", "-r", help="Component spec as string"
    )
):
    config = RunnerConfig()

    run_spec = json.loads(run_spec_str)

    runner = SplightComponentRunner(
        component_name=run_spec["name"],
        component_version=run_spec["version"],
    )
    runner.configure(config.json())
    runner.run(run_spec)


if __name__ == "__main__":
    app()
