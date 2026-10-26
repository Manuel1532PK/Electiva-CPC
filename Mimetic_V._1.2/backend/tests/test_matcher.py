"""Tests for the diagnostic matcher and negation handling.

These are pure (no DB) unit tests over the real 51-disease catalog that
ships in seed_data.py, verifying the clinical-safety properties the engine
must guarantee:

- a single generic symptom never yields a diagnosis;
- a complete symptom profile ranks its true disease first;
- denied symptoms act as negative evidence (hard penalty on cardinal ones);
- explicit denials never get registered as present;
- accent-insensitive matching works for symptom strings.
"""
import ast
import unicodedata

import pytest
from seed_data import diseases

from app.expert_system import matcher as m
from app.expert_system import normalizer as nmod
from app.expert_system import engine as eng
from app.expert_system.engine import narrow_diagnoses


def _catalog() -> list[dict]:
    return diseases


def _rank(symptoms, weights, excluded=None):
    out = []
    for d in _catalog():
        count, score = m.calculate_match(symptoms, d["symptoms"], weights, excluded)
        if score > 0:
            out.append((score, count, d["name"]))
    out.sort(reverse=True)
    return out


@pytest.fixture(scope="module")
def weights():
    return m.build_symptom_weights(_catalog())


class _FakeCol:
    def __init__(self, docs):
        self.docs = docs

    async def find_one(self, query):
        for d in self.docs:
            if all(d.get(k) == v for k, v in query.items()):
                return d
        return None

    def find(self):
        class Cursor:
            def __init__(self, docs):
                self.docs = docs

            async def to_list(self, length=None):
                return self.docs

        return Cursor(self.docs)


class _FakeDB:
    def __init__(self, docs):
        self.treatments = _FakeCol(docs)


@pytest.fixture
def fake_treatment_db():
    docs = [
        {"disease_name": "lupus eritematoso sistemico", "medicines": ["A"]},
        {"disease_name": "leptospirosis", "medicines": ["B"]},
        {"disease_name": "Amigdalitis", "medicines": ["C"]},
    ]
    return _FakeDB(docs)


class TestSingleGenericSymptomIsNeverDiagnostic:
    @pytest.mark.parametrize("symptom", [
        "dolor muscular",
        "dolor de cabeza",
        "tos",
        "fatiga",
        "fiebre",
        "vértigo",
        "dolor abdominal",
        "náuseas",
    ])
    def test_single_symptom_stays_below_candidate_bar(self, weights, symptom):
        ranked = _rank([symptom], weights)
        assert ranked, f"{symptom} should still surface low candidates"
        # Must not reach the confidence we require before presenting a
        # differential (READY_MIN_TOP_CONFIDENCE in conversation.py).
        assert ranked[0][0] < 0.5


class TestCompleteProfileRanksCorrectDisease:
    def test_gripe_full_first(self, weights):
        syms = [
            "fiebre", "tos", "dolor de garganta", "dolor muscular",
            "escalofríos", "malestar general intenso", "congestión nasal",
            "dolor de cabeza",
        ]
        ranked = _rank(syms, weights)
        top_name = ranked[0][2]
        assert top_name == "Influenza (Gripe)"
        assert ranked[0][0] > 0.5

    def test_dengue_full_first(self, weights):
        syms = [
            "fiebre alta persistente", "dolor de cabeza", "dolor muscular",
            "dolor articular", "dolor detrás de los ojos", "sarpullido",
            "petequias", "fatiga extrema",
        ]
        ranked = _rank(syms, weights)
        assert ranked[0][2] == "Dengue"
        assert ranked[0][0] > 0.5

    def test_growing_evidence_improves_gripe(self, weights):
        partial = _rank(["fiebre", "tos", "fatiga"], weights)[0][0]
        full = _rank([
            "fiebre", "tos", "dolor de garganta", "dolor muscular",
            "escalofríos", "malestar general intenso", "congestión nasal",
            "dolor de cabeza",
        ], weights)[0][0]
        assert full > partial


class TestNegativeEvidence:
    def test_denying_fever_crushes_fever_diseases(self, weights):
        # Cough with explicitly no fever: fever-dependent profiles drop hard.
        ranked = _rank(
            ["tos", "congestión nasal", "dolor de garganta", "estornudos"],
            weights,
            excluded=["fiebre"],
        )
        top_name = ranked[0][2]
        assert top_name != "Influenza (Gripe)"
        assert ranked[0][0] > 0.3  # still a sensible lead (resfriado)

    def test_excluded_cut_below_min_keeps_resfriado(self, weights):
        ranked = _rank(
            ["tos", "congestión nasal", "dolor de garganta", "estornudos"],
            weights,
            excluded=["fiebre"],
        )
        assert any("Resfriado" in name for _, _, name in ranked[:3])


class TestNormalizeNegation:
    def test_no_fiebre_is_negated_not_present(self):
        res = nmod.normalize_symptoms(["no ha tenido fiebre"])
        assert res["matched"] == []
        assert "fiebre" in res["negated"]

    def test_sin_tos_negated(self):
        res = nmod.normalize_symptoms(["sin tos"])
        assert res["matched"] == []
        assert "tos" in res["negated"]

    def test_ni_fiebre_ni_tos(self):
        neg = nmod.find_negated_symptoms("no presenta ni fiebre ni tos")
        assert "fiebre" in neg
        assert "tos" in neg

    def test_positive_sentence_not_negated(self):
        res = nmod.normalize_symptoms(["tiene fiebre y tos"])
        assert "fiebre" in res["matched"]
        assert "tos" in res["matched"]
        assert res["negated"] == []


class TestAccentInsensitiveMatching:
    def test_tos_cronica(self):
        # "tos cronica" is a canonical profile of its own.
        assert nmod.find_symptom("tos cronica") == "tos crónica"
        assert nmod.find_symptom("tos crónica") == "tos crónica"

    def test_vomito_sin_acento(self):
        assert nmod.find_symptom("vomito") == "vómito"

    def test_perdida_del_gusto(self):
        assert nmod.find_symptom("perdida del gusto") == "pérdida del gusto"


class TestNarrowDiagnosesNeverFabricates:
    def _doc(self, name, conf, symptoms, present_count):
        return {
            "disease_name": name,
            "confidence": conf,
            "matched_symptoms": present_count,
            "disease_symptoms": symptoms,
            "secondary_score": 0,
        }

    def test_all_below_threshold_returns_empty(self):
        diags = [self._doc("X", 0.10, ["a", "b"], 1)]
        assert narrow_diagnoses(diags, ["a"]) == []

    def test_keeps_clear_leader(self):
        diags = [
            self._doc("A", 0.65, ["a", "b"], 2),
            self._doc("B", 0.45, ["a", "b"], 2),
            self._doc("C", 0.30, ["a", "b"], 2),
        ]
        kept = narrow_diagnoses(diags, ["a", "b"])
        names = [d["disease_name"] for d in kept]
        assert names == ["A", "B"]

    def test_empty_input_returns_empty(self):
        assert narrow_diagnoses([self._doc("X", 0.9, ["a"], 1)], []) == []


class TestTreatmentLookupNeverGuessesDisease:
    """Regression: typing a symptom must never fetch an unrelated treatment.
    "tos" used to match "lupus eritemaTOSo sistémico" via unsafe substring
    matching in get_treatment()."""

    def test_short_or_generic_words_resolve_to_no_disease(self):
        for msg in ["tos", "fiebre", "dia", "pecho", "tos", "garganta"]:
            assert eng._resolve_disease_name(msg) is None, msg

    def test_recognized_aliases_still_resolve(self):
        assert eng._resolve_disease_name("gripe") == "Influenza"
        assert eng._resolve_disease_name("gripa") == "Influenza"
        assert eng._resolve_disease_name("neumonia") == "Neumonía"
        assert eng._resolve_disease_name("jaqueca") == "Migraña"

    def test_whole_disease_names_still_resolve(self):
        assert eng._resolve_disease_name("lupus") is None  # not aliased
        # exact name match happens downstream in get_treatment()
        assert eng._resolve_disease_name("influenza") == "Influenza"
        assert eng._resolve_disease_name("resfriado") == "Resfriado"

    def test_get_treatment_tos_not_lupus(self, fake_treatment_db):
        import asyncio

        prev = eng.get_db
        eng.get_db = lambda: fake_treatment_db
        try:
            assert asyncio.run(eng.get_treatment("tos")) is None
            # exact name match is legit; only substring guessing must never fire
            assert asyncio.run(eng.get_treatment("leptospirosis")) is not None
            assert asyncio.run(eng.get_treatment("lupus")) is not None
            assert asyncio.run(eng.get_treatment("lupus eritematoso sistemico")) is not None
            assert asyncio.run(eng.get_treatment("tengo tos")) is None
        finally:
            eng.get_db = prev