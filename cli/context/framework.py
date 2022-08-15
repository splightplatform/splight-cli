from typing import TypeVar, Callable
from splight_lib import logging
from splight_lib.settings import setup


logger = logging.getLogger()
RetType = TypeVar("RetType")
OriginalFunc = Callable[..., RetType]
DecoratedFunc = Callable[..., RetType]


class FrameworkManager:
    @property
    def setup(self):
        return setup

    def configure(self, environment):
        setup.configure(environment)
