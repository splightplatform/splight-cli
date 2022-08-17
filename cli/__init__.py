import os
from cli.cli import cli
from cli.context import *
from cli.component import *
from cli.database import *
from cli.datalake import *
from cli.deployment import *
from cli.storage import *
from cli.workspace import *
from cli.constants import SPLIGHT_PATH

os.makedirs(SPLIGHT_PATH, exist_ok=True)

__all__ = [
    cli
]