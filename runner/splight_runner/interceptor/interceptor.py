from logging import LogRecord

from splight_runner.log_streamer.log_streamer import ComponentLogsStreamer


class ApplicationLogInterceptor:
    def __init__(self):
        self._streamer = ComponentLogsStreamer(
            grpc_host="localhost:5001",
            access_id="access_id",
            secret_key="secret_key",
            component_id="1234",
        )
        self._streamer.start()

    def save_record(self, record: LogRecord):
        # TODO: Send a more complex object with message, name, level, exc_info, etc
        message = f"{record.levelname} | {record.msg}"
        if record.exc_info:
            message += f" | {record.exc_text}"
        self._streamer.insert_message(message)


interceptor = ApplicationLogInterceptor()
