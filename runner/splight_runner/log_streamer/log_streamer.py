from queue import Empty, Queue
from threading import Thread, Lock
from typing import Generator, Optional

from splight_runner.grpc.client import LogsGRPCClient, LogsGRPCError


class LogsStreamerError(Exception):
    pass


class ComponentLogsStreamer:
    def __init__(
        self,
        grpc_host: str,
        access_id: str,
        secret_key: str,
        component_id: Optional[str] = None,
    ):
        self._component_id = component_id

        try:
            self._client = self._create_client(
                grpc_host, access_id, secret_key
            )
        except Exception as exc:
            raise LogsStreamerError(
                "Unable to connect to gRPC server"
            ) from exc
        self._logs_entry = self._client._log_entry
        self._thread: Optional[Thread] = None
        self._queue: Optional[Queue] = None
        self._lock = Lock()
        self._running: bool = False

    def _create_client(self, grpc_host: str, access_id: str, secret_key: str):
        client = LogsGRPCClient(
            grpc_host=grpc_host, secure_channel=False
        )
        client.set_authorization_header(
            access_id=access_id,
            secret_key=secret_key,
        )
        return client

    def insert_message(self, message: str):
        if not self._queue:
            raise Exception("Queue is none")
        with self._lock:
            self._queue.put(message)

    def start(self):
        print("Starting")
        self._thread = Thread(target=self._run, daemon=True)
        self._queue = Queue()
        self._running = True
        self._thread.start()

    def stop(self):
        self._running = False
        self._thread.join(timeout=10)
        self._queue = None
        self._thread = None

    def _run(self):
        while self._running:
            try:
                self._client.stream_logs(
                    self.logs_iterator, self._component_id
                )
            except LogsGRPCError as exc:
                raise LogsStreamerError(
                    "Component Logs stream stopped"
                ) from exc

    def logs_iterator(self) -> Generator:
        while True:
            try:
                message = self._queue.get(timeout=10)
            except Empty:
                return

            yield message
