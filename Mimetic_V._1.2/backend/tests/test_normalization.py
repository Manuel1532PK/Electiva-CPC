from unittest.mock import AsyncMock, MagicMock
from bson import ObjectId

from app.utils import normalize_text
from import_from_excel import _split_symptoms
from seed_data import dedupe_collection


class _FakeCursor:
    def __init__(self, docs):
        self.docs = docs

    async def to_list(self, length=None):
        return self.docs


class TestNormalizeText:
    def test_quita_espacios_y_minusculas(self):
        assert normalize_text("  VÓMITO ") == "vomito"

    def test_quita_diacriticos(self):
        assert normalize_text("Vómito") == "vomito"
        assert normalize_text("vomito") == "vomito"
        assert normalize_text("pérdida del olfato") == "perdida del olfato"
        assert normalize_text("náuseas") == "nauseas"

    def test_converge_variantes(self):
        variantes = " VÓMITO ", "Vómito", "vomito", "VOMITO "
        normalizadas = {normalize_text(v) for v in variantes}
        assert normalizadas == {"vomito"}

    def test_valores_no_textuales(self):
        assert normalize_text(None) == ""
        assert normalize_text(123) == "123"


class TestSplitSymptoms:
    def test_deduplica_y_normaliza(self):
        partes = _split_symptoms("Fiebre|fiebre|FIEBRE|Vómito")
        assert partes == ["fiebre", "vomito"]

    def test_acepta_lista(self):
        partes = _split_symptoms(["Dolor", "dolor", "Náuseas"])
        assert partes == ["dolor", "nauseas"]

    def test_ignora_vacios(self):
        assert _split_symptoms("") == []
        assert _split_symptoms("tos|   |fiebre") == ["tos", "fiebre"]


class TestDedupeCollection:
    def _make_doc(self, i, key):
        return {"_id": ObjectId(f"{i:024x}"), "name": key}

    def _collection_with(self, docs):
        collection = MagicMock()
        collection.find.return_value = _FakeCursor(docs)
        collection.delete_many = AsyncMock()
        collection.update_one = AsyncMock()
        return collection

    async def test_colapsa_variantes_con_acento(self):
        collection = self._collection_with([
            self._make_doc(1, "Vómito"),
            self._make_doc(2, "vomito"),
            self._make_doc(3, "vomito"),
        ])
        removed = await dedupe_collection(collection, "name")

        assert removed == 2
        delete_call = collection.delete_many.await_args
        assert len(delete_call.args[0]["_id"]["$in"]) == 2
        assert collection.update_one.await_args.args[1] == {"$set": {"name": "vomito"}}

    async def test_colapsa_duplicados_exactos(self):
        collection = self._collection_with([
            self._make_doc(1, "fiebre"),
            self._make_doc(2, "fiebre"),
            self._make_doc(3, "fiebre"),
        ])
        removed = await dedupe_collection(collection, "name")
        assert removed == 2
        delete_ids = collection.delete_many.await_args.args[0]["_id"]["$in"]
        assert len(delete_ids) == 2

    async def test_sin_duplicados_no_borra(self):
        collection = self._collection_with([
            self._make_doc(1, "fiebre"),
            self._make_doc(2, "tos"),
            self._make_doc(3, "nauseas"),
        ])
        removed = await dedupe_collection(collection, "name")
        assert removed == 0
        collection.delete_many.assert_not_awaited()
        collection.update_one.assert_not_awaited()
