import logging
from typing import Callable

from splight_runner.interceptor.interceptor import interceptor


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
        # interceptor.save_record(record)
        print("Handling record")
        return func(self, record)

    return wrapped
