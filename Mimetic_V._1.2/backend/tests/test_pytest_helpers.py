from unittest.mock import AsyncMock

import pytest

from app.database.mongodb import _strip_insecure_params
from seed_data import _upsert_many


class TestStripInsecureParams:
    def test_elimina_tls_insecure(self):
        url = "mongodb://host:27017/mimetic?tls=true&tlsInsecure=true"
        assert "tlsInsecure" not in _strip_insecure_params(url)

    def test_elimina_cert_invalidos(self):
        url = "mongodb+srv://host/db?tlsAllowInvalidCertificates=true&tlsAllowInvalidHostnames=true"
        cleaned = _strip_insecure_params(url)
        assert "tlsAllowInvalidCertificates" not in cleaned
        assert "tlsAllowInvalidHostnames" not in cleaned

    def test_limpia_signos_duplicados(self):
        url = "mongodb://host/db?tls=true&&tlsInsecure=true"
        assert "&&" not in _strip_insecure_params(url)

    def test_url_limpia_se_mantiene(self):
        assert _strip_insecure_params("mongodb://host:27017/db") == "mongodb://host:27017/db"


@pytest.mark.asyncio
async def test_upsert_many_ignora_docs_sin_clave():
    collection = AsyncMock()
    documents = [{"name": "fiebre"}, {"descripcion": "sin clave"}, {"name": "tos"}]

    count = await _upsert_many(collection, documents, "name")

    assert len(documents) == 3
    assert count == 2
    assert collection.update_one.await_count == 2


@pytest.mark.asyncio
async def test_upsert_many_usa_upsert_con_set_y_filtro_por_clave():
    collection = AsyncMock()
    documents = [{"_id": "viejo", "name": "fiebre", "severity": "mild"}]

    count = await _upsert_many(collection, documents, "name")

    assert count == 1
    call = collection.update_one.await_args
    assert call.args[0] == {"name": "fiebre"}
    assert call.args[1] == {"$set": {"name": "fiebre", "severity": "mild"}}
    call.kwargs["upsert"] is True or call.await_kwargs.get("upsert") is True