from itertools import cycle
from shutil import get_terminal_size
from threading import Thread
from time import sleep
from typing import Optional

from colorama import Fore, Style


class Loader:
    def __init__(
        self,
        desc: str = "Loading...",
        end: Optional[str] = None,
        timeout: float = 0.1,
        msg: Optional[str] = None,
    ):
        """
        A loader-like context manager

        Args:
            desc (str, optional): The loader's description. Defaults to "Loading...".
            end (str, optional): Final print. Defaults to None.
            timeout (float, optional): Sleep time between prints. Defaults to 0.1.
            msg (str, optional): Custom message to print when stopping. Defaults to None.
        """
        self.desc = desc
        self.end = end if end is not None else "Done!"
        self.timeout = timeout
        self.msg = msg

        self._thread = Thread(target=self._animate, daemon=True)
        self.steps = ["⢿", "⣻", "⣽", "⣾", "⣷", "⣯", "⣟", "⡿"]
        self.done = False

    def start(self):
        self._thread.start()
        return self

    def _animate(self):
        for c in cycle(self.steps):
            if self.done:
                break
            print(
                f"\r{c} {Fore.BLUE}{self.desc}{Style.RESET_ALL} ",
                flush=True,
                end="",
            )
            sleep(self.timeout)

    def __enter__(self):
        self.start()

    def stop(self):
        self.done = True
        cols = get_terminal_size((80, 20)).columns
        print("\r" + " " * cols, end="", flush=True)
        if self.msg is not None:
            print(f"\r{self.msg}", flush=True)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.stop()
            raise exc_type(*exc_val.args)
        self.stop()
