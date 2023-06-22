import subprocess
from traceback import print_tb
from typing import Iterator, List, Tuple
import grpc
from . import logs_pb2
from . import logs_pb2_grpc
from google.protobuf.timestamp_pb2 import Timestamp
from datetime import datetime
from splight_lib.settings import settings
from google.protobuf.descriptor_pool import DescriptorPool
from grpc_reflection.v1alpha.proto_reflection_descriptor_database import ProtoReflectionDescriptorDatabase


class ComponentLogsHandler:
    def __init__(self, process: subprocess.Popen) -> None:
        self.process = process

    @property
    def metadata(self) -> List[Tuple[str, str]]:
        metadata = [(
            "authorization", (
                    f'Splight '
                    f'{settings.SPLIGHT_ACCESS_ID} '
                    f'{settings.SPLIGHT_SECRET_KEY}')
        ),]
        return metadata

    def _parse_line(self, line: bytes) -> logs_pb2.LogEntry:
        message = line.decode("utf-8").rstrip()
        timestamp = Timestamp(
            seconds=int(datetime.now().timestamp())
        )
        return logs_pb2.LogEntry(
            message=message,
            timestamp=timestamp
        )

    def logs_iterator(self) -> Iterator[logs_pb2.LogEntry]:
        for line in self.process.stdout:
            yield self._parse_line(line)

    def start(self) -> None:
        with grpc.insecure_channel(settings.SPLIGHT_GRPC_API_HOST) as channel:

            """
            reflection_db = ProtoReflectionDescriptorDatabase(channel)
            descriptor_pool = DescriptorPool(reflection_db)
            service_descriptor = descriptor_pool.FindServiceByName("LogsService")
            method_descriptor = service_descriptor.FindMethodByName("StashLogEntry")
            """
            stub = logs_pb2_grpc.LogsServiceStub(channel)
            stub.StashLogEntry(self.logs_iterator(), metadata=self.metadata)
