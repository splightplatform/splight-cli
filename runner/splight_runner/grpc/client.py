from typing import Callable, Optional, Tuple

import grpc

# from splight_runner.grpc.reflector import GrpcReflectionClient
from splight_runner.grpc.logs_pb2 import LogEntry
from splight_runner.grpc.logs_pb2_grpc import LogsServiceStub


class LogsGRPCError(Exception):
    pass


class MissingGRPCService(Exception):
    pass


class SplightGRPCClient:
    AUTHORIZATION: str = "authorization"
    _SERVICE_NAME: str = None

    def __init__(self, grpc_host: str, secure_channel: bool = True):
        if not self._SERVICE_NAME:
            raise MissingGRPCService("Missing parameter service_name")

        if secure_channel:
            self._channel = grpc.secure_channel(
                grpc_host, grpc.ssl_channel_credentials()
            )
        else:
            self._channel = grpc.insecure_channel(grpc_host)

        self._stub = LogsServiceStub(self._channel)
        self._auth_header: Optional[Tuple[str, str]] = None

    def set_authorization_header(self, access_id: str, secret_key: str):
        self._auth_header = (
            SplightGRPCClient.AUTHORIZATION,
            f"Splight {access_id} {secret_key}",
        )


class LogsGRPCClient(SplightGRPCClient):
    _SERVICE_NAME: str = "LogsService"
    _LOG_ENTRY: str = "LogEntry"

    def __init__(self, grpc_host: str, secure_channel: bool = True):
        super().__init__(grpc_host, secure_channel=secure_channel)
        self._log_entry = LogEntry

    # @retry_streaming(times=5)
    def stream_logs(self, log_generator: Callable, component_id: str):
        try:
            self._stub.stash_log_entry(
                self._parse_log_message(log_generator(), component_id),
                metadata=[self._auth_header],
            )
        except grpc.RpcError as exc:
            raise LogsGRPCError("Unable to stream component logs") from exc

    def _parse_log_message(self, message_iterator: str, component_id: str):
        for message in message_iterator:
            yield self._log_entry(
                message=message,
                component_id=component_id,
            )
