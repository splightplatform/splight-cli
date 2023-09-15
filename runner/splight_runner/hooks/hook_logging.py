import logging
from types import ModuleType
from typing import Callable
from splight_runner.interceptor.interceptor import interceptor

import importhook


def call_handlers_wrapper(func: Callable) -> Callable:
    """Wrapper for callHandlers method of the Logger class.

    Parameters
    ----------
    func: Callable
        The original callHandlers method.

    Returns
    -------
    Callable: The wrapped callHandlers method with extra functionality.
    """

    def wrapped(self, record: logging.LogRecord) -> None:
        """Modifies the method callHandlers in order to send the log message
        to the log service.
        """
        # Do custom logic
        interceptor.save_record(record)
        return func(self, record)

    return wrapped


@importhook.on_import("logging")
def on_logging_import(module: ModuleType) -> ModuleType:
    """Hook for modifying default behavior for the logging module.

    Parameters
    ----------
    module: ModuleType
        The built-in logging module

    Returns
    -------
    ModuleType: The logging module updated
    """
    original = getattr(module.Logger, "callHandlers", None)
    # Check if spl runner is active
    if original:
        wrapped = call_handlers_wrapper(original)
        new_module = importhook.copy_module(logging)
        setattr(new_module.Logger, "callHandlers", wrapped)
        return new_module
    return module


# Reload logging module to update everywhere
importhook.reload_module(logging)
