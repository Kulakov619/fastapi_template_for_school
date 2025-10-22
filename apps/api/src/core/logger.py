import contextvars
import datetime
import json
import logging
import socket

from core.config import settings

request_id_var = contextvars.ContextVar("request_id", default=None)


class RequestIdFilter(logging.Filter):
    def filter(self, record):
        request_id = request_id_var.get()
        record.request_id = request_id if request_id else "N/A"
        return True


class JsonUdpHandler(logging.Handler):
    def __init__(self, host=settings.logstash_host, port=settings.logstash_port):
        super().__init__()
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def emit(self, record):
        try:
            log_entry = self.format(record)
            self.sock.sendto(log_entry.encode(), (self.host, self.port))
        except Exception:
            self.handleError(record)


class JsonFormatter(logging.Formatter):
    def format(self, record):
        current_time = datetime.datetime.utcnow()
        timestamp_str = current_time.strftime("%Y.%m.%d")
        index_value = f"auth_api-{timestamp_str}"
        log_record = {
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "timestamp": self.formatTime(record),
            "filename": record.filename,
            "funcName": record.funcName,
            "lineno": record.lineno,
            "request_id": getattr(record, "request_id", "N/A"),
            "index": index_value
        }
        if record.exc_info:
            log_record["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(log_record)


def setup_logger():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    handler = JsonUdpHandler()
    formatter = JsonFormatter()
    handler.setFormatter(formatter)
    handler.addFilter(RequestIdFilter())
    logger.addHandler(handler)

    for h in logger.handlers:
        if isinstance(h, logging.StreamHandler):
            logger.removeHandler(h)
