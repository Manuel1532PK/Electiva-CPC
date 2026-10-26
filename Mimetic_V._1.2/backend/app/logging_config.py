import json
import logging
import os
import time
import uuid
from contextvars import ContextVar

from starlette.middleware.base import BaseHTTPMiddleware

_REQUEST_ID: ContextVar[str] = ContextVar("request_id", default="-")

RESERVED_LOGGER_NAMES = {"mimetic.http", "mimetic.mongodb", "mimetic.main"}


class StructuredFormatter(logging.Formatter):
    """Formatea cada registro como una línea JSON con los campos clave."""

    def format(self, record: logging.LogRecord) -> str:
        base = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": _REQUEST_ID.get(),
        }
        if record.exc_info:
            base["exc"] = self.formatException(record.exc_info)
        extra = getattr(record, "extra_fields", None)
        if isinstance(extra, dict):
            base.update(extra)
        return json.dumps(base, ensure_ascii=False)


def setup_logging():
    """Configura el loggeo estructurado en el root logger (idempotente)."""
    handler = logging.StreamHandler()
    handler.setFormatter(StructuredFormatter())
    root = logging.getLogger()
    # Evita duplicar handlers si se llama varias veces (TestClient reutiliza el proceso)
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(os.getenv("LOG_LEVEL", "INFO").upper())


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


class LogContextMiddleware(BaseHTTPMiddleware):
    """Asigna un request_id por petición y registra método, ruta, status y duración."""

    async def dispatch(self, request, call_next):
        request_id = uuid.uuid4().hex[:12]
        token = _REQUEST_ID.set(request_id)
        start = time.perf_counter()
        status = 500
        response = None
        try:
            response = await call_next(request)
            status = response.status_code
            response.headers["X-Request-ID"] = request_id
        except Exception:
            get_logger("mimetic.http").error(
                "unhandled exception",
                exc_info=True,
                extra={"extra_fields": {
                    "method": request.method,
                    "path": request.url.path,
                    "request_id": request_id,
                }},
            )
            raise
        finally:
            duration_ms = round((time.perf_counter() - start) * 1000, 2)
            get_logger("mimetic.http").info(
                "request completed",
                extra={"extra_fields": {
                    "method": request.method,
                    "path": request.url.path,
                    "status": status,
                    "duration_ms": duration_ms,
                    "request_id": request_id,
                    "client": request.client.host if request.client else "-",
                }},
            )
            _REQUEST_ID.reset(token)
        return response