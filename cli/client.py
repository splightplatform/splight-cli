from functools import wraps
from typing import TypeVar, Callable
from splight_lib.settings import setup
from splight_lib import logging

RetType = TypeVar("RetType")
OriginalFunc = Callable[..., RetType]
DecoratedFunc = Callable[..., RetType]

logger = logging.getLogger()


class SplightClient:
    def _set_fake_setup(self):
        setup.configure({
            "DATABASE_CLIENT": "fake_splight_lib.database.FakeDatabaseClient",
            "DATALAKE_CLIENT": "fake_splight_lib.datalake.FakeDatalakeClient",
            "STORAGE_CLIENT": "fake_splight_lib.storage.FakeStorageClient",
        })
        logger.debug(f"Using new setup {setup}")

    def _set_remote_setup(self):
        setup.configure({
            "DATABASE_CLIENT": "remote_splight_lib.database.DatabaseClient",
            "DATALAKE_CLIENT": "remote_splight_lib.datalake.DatalakeClient",
            "STORAGE_CLIENT": "remote_splight_lib.storage.StorageClient",
        })
        logger.debug(f"Using new setup {setup}")


def remotely_available(func: OriginalFunc) -> DecoratedFunc:
    @wraps(func)
    def wrapper(self, *args, **kwargs) -> RetType:
        remote = kwargs.pop('remote', False)
        if remote:
            self._set_remote_setup()
        return func(self, *args, **kwargs)
    return wrapper