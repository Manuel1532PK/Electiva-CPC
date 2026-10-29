import io
import json
import logging
from unittest.mock import AsyncMock, Mock, patch

from starlette.testclient import TestClient

from app.logging_config import StructuredFormatter


def _capture_root_log():
    buffer = io.StringIO()
    handler = logging.StreamHandler(buffer)
    handler.setFormatter(StructuredFormatter())
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(logging.INFO)
    return buffer, handler


class _FakeClient:
    def __init__(self, db_mock):
        self._db = db_mock

    def __getitem__(self, name):
        return self._db

    def close(self):
        pass


def _fake_mongo_client():
    db_mock = Mock()
    db_mock.command = AsyncMock(return_value=1)
    db_mock.symptoms = Mock()
    db_mock.symptoms.update_one = AsyncMock()
    db_mock.diseases = Mock()
    db_mock.diseases.update_one = AsyncMock()
    db_mock.treatments = Mock()
    db_mock.treatments.update_one = AsyncMock()
    client_inst = _FakeClient(db_mock)
    return client_inst


def test_health_conecta_seeded_y_registra_json_con_request_id():
    import main

    buffer, handler = _capture_root_log()
    try:
        with (
            patch("app.database.mongodb.AsyncIOMotorClient", return_value=_fake_mongo_client()),
            patch("app.database.mongodb.create_indexes", new_callable=AsyncMock),
        ):
            with TestClient(main.app) as client:
                res = client.get("/health")

        assert res.status_code == 200
        assert res.json()["status"] == "ok"
        assert res.headers["X-Request-ID"]

        lines = buffer.getvalue().strip().splitlines()
        http_log = [json.loads(l) for l in lines if 'request completed' in json.loads(l)["message"]]
        assert len(http_log) == 1
        entry = http_log[0]
        assert entry["method"] == "GET"
        assert entry["path"] == "/health"
        assert entry["status"] == 200
        assert entry["request_id"] == res.headers["X-Request-ID"]
    finally:
        logging.getLogger().handlers.remove(handler)


def test_health_degradado_cuando_mongo_no_conecta():
    import main

    buffer, handler = _capture_root_log()
    try:
        with (
            patch("app.database.mongodb.AsyncIOMotorClient", return_value=Mock()),
            patch("app.database.mongodb.asyncio.sleep", new_callable=AsyncMock),
        ):
            with TestClient(main.app) as client:
                res = client.get("/health")

        assert res.status_code == 200
        assert res.json()["status"] == "degraded"
        assert res.json()["database"] == "disconnected"
        assert res.headers["X-Request-ID"]
    finally:
        logging.getLogger().handlers.remove(handler)


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-v"]))