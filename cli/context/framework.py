from typing import Callable, TypeVar

from splight_lib import logging
from splight_lib.settings import setup

logger = logging.getLogger()
RetType = TypeVar("RetType")
OriginalFunc = Callable[..., RetType]
DecoratedFunc = Callable[..., RetType]


class MissingConfiguration(Exception):
    pass


class FrameworkManager:
    @property
    def setup(self):
        return setup

    def configure(self, environment):
        empty_keys = [
            key for key, value in environment.items() if value is None
        ]
        if empty_keys:
            raise MissingConfiguration(
                f"Please run `splightcli configure` and set keys {empty_keys}"
            )
        setup.configure(environment)
