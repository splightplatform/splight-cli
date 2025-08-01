import os

API_VERSION = os.getenv("API_VERSION", "v3")

import typer  # noqa: E402

if API_VERSION == "v3":
    from splight_cli.engine.alert import alert_app

from splight_cli.engine.asset import asset_app  # noqa: E402
from splight_cli.engine.attribute import attribute_app  # noqa: E402
from splight_cli.engine.component import component_app  # noqa: E402
from splight_cli.engine.datalake import datalake_app  # noqa: E402
from splight_cli.engine.file import file_app  # noqa: E402
from splight_cli.engine.secret import secret_app  # noqa: E402

engine_app = typer.Typer(
    name="Splight Engine",
    add_completion=True,
    rich_markup_mode="rich",
    no_args_is_help=True,
)

if API_VERSION == "v3":
    engine_app.add_typer(alert_app, name="alert")
engine_app.add_typer(asset_app, name="asset")
engine_app.add_typer(attribute_app, name="attribute")
engine_app.add_typer(component_app, name="component")
engine_app.add_typer(datalake_app, name="datalake")
engine_app.add_typer(file_app, name="file")
engine_app.add_typer(secret_app, name="secret")
