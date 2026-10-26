import math
import unicodedata

# Confidence/hyper-parameters for the diagnostic matching heuristic.
# Tuned so that a single generic symptom never yields a usable diagnosis,
# while a near-complete symptom profile reaches a high, decisive score.

# A disease needs at least this many matching symptoms to be taken seriously.
# Below it, the score is heavily penalized (and hard-capped) to avoid
# "1 symptom => diagnosis".
SINGLE_MATCH_PENALTY = 0.30
SINGLE_MATCH_CAP = 0.26
MISSING_CARDINAL_EXCLUDED_FACTOR = 0.15
EXCLUDED_WEAK_FACTOR = 0.45
CARDINAL_WEIGHT = 2.0  # symptoms with weight >= this are treated as cardinal

# Exponents that shape the balance between coverage (how much of the disease
# is present) and specificity (how well the disease explains the evidence).
COVERAGE_EXP = 0.8
SPECIFICITY_EXP = 0.5


def _norm(s: str) -> str:
    """Lowercase, strip whitespace and remove accents for robust matching.

    Patients (and the UI) often type symptoms without diacritics ("vomito"
    instead of "vómito"); using accent-folded keys makes the matcher tolerant.
    """
    s = s.strip().lower()
    nfkd = unicodedata.normalize("NFKD", s)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def build_symptom_weights(diseases: list[dict]) -> dict[str, float]:
    """Compute an Inverse Document Frequency (IDF)-like weight per symptom.

    Symptoms shared by very few diseases (specific/cardinal) get a high weight;
    symptoms present across many diseases (generic like "fatiga") get a weight
    close to 1. The weights keep the raw log-scale (with smoothing) so the
    ranking stays stable as the disease catalog grows; adding more diseases
    naturally re-tunes the weights without needing to re-normalize ranges.

    Weight = 1 + log((N + 1)/(df + 1))  -> ~1 for ubiquitous symptoms,
    strictly larger for rare ones.
    """
    n_diseases = len(diseases)
    if n_diseases == 0:
        return {}

    doc_freq: dict[str, int] = {}
    for disease in diseases:
        seen = set()
        for s in disease.get("symptoms", []):
            sym = _norm(s)
            if sym and sym not in seen:
                seen.add(sym)
                doc_freq[sym] = doc_freq.get(sym, 0) + 1

    weights: dict[str, float] = {}
    for sym, count in doc_freq.items():
        weights[sym] = round(1.0 + math.log((n_diseases + 1) / (count + 1)), 4)

    return weights


def _excluded_penalty(excluded: set[str], disease_set: set[str], weights: dict) -> float:
    """Compute a multiplicative penalty for explicitly denied symptoms.

    If the doctor states a symptom is absent and that symptom is part of the
    disease profile, the disease becomes much less likely. Cardinal symptoms
    (rare/highly specific ones) hit harder than generic ones, but nothing is
    ever hard-excluded, keeping the system a "proposal" rather than a verdict.
    """
    if not excluded or not disease_set:
        return 1.0
    factor = 1.0
    for x in excluded & disease_set:
        wx = weights.get(x, 1.0)
        if wx >= CARDINAL_WEIGHT:
            factor *= MISSING_CARDINAL_EXCLUDED_FACTOR
        else:
            factor *= EXCLUDED_WEAK_FACTOR
    return max(factor, 0.01)


def calculate_match(
    symptoms_input: list[str],
    disease_symptoms: list[str],
    weights: dict[str, float] | None = None,
    excluded_input: list[str] | None = None,
) -> tuple[int, float]:
    """Score how well a disease explains the presented symptoms.

    Returns (matched_count, confidence).
    - ``coverage``    = weighted fraction of the disease profile present
                        (rewards diseases that explain a large share of their
                        own expected symptoms).
    - ``specificity`` = weighted fraction of the patient's symptoms that the
                        disease actually has (penalizes diseases that do not
                        explain part of the evidence).
    - A single matching symptom is penalized hard so a diagnosis is never
      proposed from one generic complaint.
    - Explicitly denied symptoms (``excluded_input``) multiply the score down.
    """
    input_set = set(_norm(s) for s in symptoms_input)
    disease_set = set(_norm(d) for d in disease_symptoms)

    if not input_set or not disease_set:
        return 0, 0.0

    matches = input_set & disease_set
    matched_count = len(matches)

    if matched_count == 0:
        return 0, 0.0

    if weights:
        matched_weight = sum(weights.get(m, 1.0) for m in matches)
        input_weight = sum(weights.get(m, 1.0) for m in input_set)
        disease_weight = sum(weights.get(m, 1.0) for m in disease_set)

        if input_weight <= 0 or disease_weight <= 0:
            return matched_count, 0.0

        coverage = matched_weight / disease_weight
        specificity = matched_weight / input_weight
        score = min(1.0, (coverage ** COVERAGE_EXP) * (specificity ** SPECIFICITY_EXP))
    else:
        # Fallback: plain ratio x coverage (backward compatible)
        ratio = matched_count / len(input_set)
        coverage = matched_count / len(disease_set) if disease_set else 0
        score = min(1.0, ratio * coverage)

    # Evidence floor: one matching symptom is rarely diagnostic. Cap it so a
    # single generic complaint can never surface as a differential.
    if matched_count < 2:
        score = min(score * SINGLE_MATCH_PENALTY, SINGLE_MATCH_CAP)

    if excluded_input:
        excluded = set(_norm(e) for e in excluded_input)
        score *= _excluded_penalty(excluded, disease_set, weights or {})

    return matched_count, round(min(score, 1.0), 3)