import io
import json
import logging

from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.testclient import TestClient

from app.logging_config import (
    LogContextMiddleware,
    StructuredFormatter,
    _REQUEST_ID,
    get_logger,
    setup_logging,
)


def test_structured_formatter_emite_json():
    fmt = StructuredFormatter()
    rec = logging.LogRecord("app.test", logging.INFO, "f.py", 3, "hola %s", ("mundo",), None)

    data = json.loads(fmt.format(rec))

    assert data["message"] == "hola mundo"
    assert data["level"] == "INFO"
    assert data["logger"] == "app.test"
    assert data["request_id"] == "-"
    assert "timestamp" in data


def test_structured_formatter_incluye_campos_extra():
    fmt = StructuredFormatter()
    rec = logging.LogRecord("app.test", logging.WARNING, "f.py", 3, "boom", (), None)
    rec.__dict__["extra_fields"] = {"method": "POST", "status": 500}

    data = json.loads(fmt.format(rec))

    assert data["method"] == "POST"
    assert data["status"] == 500


def test_setup_logging_idempotente():
    setup_logging()
    setup_logging()

    root = logging.getLogger()
    assert len(root.handlers) == 1
    assert isinstance(root.handlers[0].formatter, StructuredFormatter)


async def _ping_route(request):
    return JSONResponse({"ok": True})


def test_middleware_asigna_request_id_y_registra_estructura():
    app = Starlette(routes=[Route("/ping", _ping_route)])
    app.add_middleware(LogContextMiddleware)

    buffer = io.StringIO()
    handler = logging.StreamHandler(buffer)
    handler.setFormatter(StructuredFormatter())
    http_log = get_logger("mimetic.http")
    http_log.handlers.append(handler)
    http_log.propagate = False
    http_log.setLevel(logging.INFO)
    try:
        with TestClient(app) as client:
            res = client.get("/ping")

        assert res.status_code == 200
        rid = res.headers["X-Request-ID"]
        assert rid and len(rid) == 12

        emitted = buffer.getvalue().strip().splitlines()
        assert len(emitted) == 1
        record = json.loads(emitted[-1])
        assert record["request_id"] == rid
        assert record["message"] == "request completed"
        assert record["method"] == "GET"
        assert record["path"] == "/ping"
        assert record["status"] == 200
        assert record["duration_ms"] >= 0
    finally:
        http_log.handlers.remove(handler)
        http_log.propagate = True


def test_contextvar_default_es_dash():
    assert _REQUEST_ID.get() == "-"