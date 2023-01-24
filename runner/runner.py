import json
import typer
import subprocess
from asyncio.log import logging
from typing import Dict, List
from pydantic import BaseModel, BaseSettings, validator, Extra, Field

app = typer.Typer(name="Splight Component Runner")


class RunnerSpec(BaseModel):
    name: str
    version: str
    input: List[Dict]

    class Config:
        extra = Extra.allow


class RunnerConfig(BaseSettings):
    NAMESPACE: str
    SPLIGHT_ACCESS_ID: str
    SPLIGHT_SECRET_KEY: str
    SPLIGHT_PLATFORM_API_HOST: str
    COMPONENT_ID: str

    class Config:
        secrets_dir: str = "/etc/config"

    @validator("SPLIGHT_PLATFORM_API_HOST")
    def remove_trailing_slash(cls, value):
        return value.rstrip("/")


class SplightComponentRunner:

    _BASE_CMD = "splightcli"

    def __init__(self):
        logging.basicConfig(
            level=logging.INFO, format="%(asctime)s - %(name)s - %(message)s"
        )
        self._logger = logging.getLogger("Splight Runner")
        self._component_id = None

    def configure(self, config: RunnerConfig):
        self._component_id = config.COMPONENT_ID
        try:
            self._logger.info("Configuring splightcli")
            subprocess.run(
                [self._BASE_CMD, "configure", "--from-json", config.json()],
                check=True,
            )
        except subprocess.CalledProcessError as exc:
            self._logger.error(f"Error configuring component: {exc}")
            self._logger.error(f"Stdout: {exc.stdout}")
            self._logger.error(f"Stderr: {exc.stderr}")
            exit(1)

    def run(self, component_spec: RunnerSpec):
        try:
            self._logger.info("Running component")
            component_name = f"{component_spec.name}/{component_spec.version}"
            subprocess.run(
                [
                    self._BASE_CMD,
                    "component",
                    "run",
                    component_name,
                    "--input",
                    json.dumps(component_spec.input),
                    "--component-id",
                    self._component_id
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
    run_spec = RunnerSpec.parse_obj(json.loads(run_spec_str))
    runner = SplightComponentRunner()
    runner.configure(config)
    runner.run(run_spec)


if __name__ == "__main__":
    app()
