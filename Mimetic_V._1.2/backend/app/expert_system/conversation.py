"""Conversational engine for interactive diagnosis."""

from app.expert_system.engine import diagnose, merge_vital_symptoms
from app.database.mongodb import get_db

MAX_CANDIDATES_FOR_SUGGESTIONS = 5
TARGET_DIAGNOSES_COUNT = 3
MAX_FOLLOWUP_SUGGESTIONS = 4

# Confidence below which the leader is not considered "anchored": until then
# the system only asks symptom descriptors the candidates have in common, so
# questions never jump to exotic symptoms of marginal candidates.
QUESTION_SOURCE_FLOOR = 0.10

# Confidence gating before the system offers a "proposal for confirmation".
# The AI never states a definitive diagnosis; it only presents differentials.
READY_MIN_TOP_CONFIDENCE = 0.50   # a single clear leader must clear this
READY_HIGH_CONFIDENCE = 0.60
READY_MIN_GAP = 0.12              # and be this far above the runner-up


def _prettify_symptom(raw: str) -> str:
    raw = raw.strip()
    if not raw.lower().startswith("dolor"):
        return raw
    rest = raw[5:].strip()
    if rest.lower().startswith("de "):
        return f"Dolor de {rest[3:].strip()}"
    if rest.lower().startswith("en "):
        # "dolor en el pecho" must stay "Dolor en el pecho", never
        # "Dolor de el pecho".
        return f"Dolor {rest}"
    return f"Dolor {rest}"


_SPECIFIC_QUESTIONS: dict[str, str] = {
    "fiebre": "¿Ha tenido fiebre?",
    "fiebre alta": "¿Ha tenido fiebre mayor a 39°C?",
    "fiebre alta persistente": "¿Ha tenido fiebre mayor a 39°C?",
    "tos": "¿Tiene tos?",
    "tos seca": "¿Tiene tos seca?",
    "tos con flema": "¿Tiene tos con flema?",
    "tos productiva": "¿Tiene tos con flema?",
    "expectoracion": "¿Tiene tos con flema (expectoración)?",
    "expectoración": "¿Tiene tos con flema (expectoración)?",
    "sibilancias": "¿Ha notado silbido al respirar (sibilancias)?",
    "mialgias": "¿Tiene dolor muscular (mialgias)?",
    "dificultad para tragar": "¿Tiene dificultad para tragar?",
    "inflamacion de amigdalas": "¿Tiene inflamadas las amígdalas?",
    "inflamación de amígdalas": "¿Tiene inflamadas las amígdalas?",
    "dolor de cabeza": "¿El dolor de cabeza es pulsátil o de tipo opresivo?",
    "dolor de cabeza intenso": "¿El dolor de cabeza es pulsátil o de tipo opresivo?",
    "cefalea": "¿El dolor de cabeza es pulsátil o de tipo opresivo?",
    "dolor detras de los ojos": "¿Presenta dolor detrás de los ojos?",
    "dolor retroocular": "¿Presenta dolor detrás de los ojos?",
    "dolor de garganta": "¿Tiene dolor de garganta?",
    "dolor abdominal": "¿El dolor abdominal es tipo cólico o constante?",
    "dolor muscular": "¿Tiene dolor muscular generalizado?",
    "mialgia": "¿Tiene dolor muscular generalizado?",
    "dolor en las articulaciones": "¿Tiene dolor en las articulaciones?",
    "artralgia": "¿Tiene dolor en las articulaciones?",
    "rigidez en el cuello": "¿Tiene rigidez en el cuello?",
    "rigidez de nuca": "¿Tiene rigidez en el cuello?",
    "fatiga": "¿Se ha sentido fatigado o con cansancio extremo?",
    "debilidad": "¿Ha sentido debilidad generalizada?",
    "perdida del gusto": "¿Ha perdido el sentido del gusto?",
    "perdida del olfato": "¿Ha perdido el sentido del olfato?",
    "anosmia": "¿Ha perdido el sentido del olfato?",
    "ageusia": "¿Ha perdido el sentido del gusto?",
    "congestion nasal": "¿Tiene congestión nasal?",
    "secrecion nasal": "¿Tiene secreción nasal?",
    "rinorrea": "¿Tiene secreción nasal?",
    "estornudos": "¿Ha estado estornudando frecuentemente?",
    "dificultad para respirar": "¿Tiene dificultad para respirar?",
    "disnea": "¿Tiene dificultad para respirar?",
    "opresion en el pecho": "¿Siente opresión en el pecho?",
    "dolor en el pecho": "¿Siente dolor en el pecho?",
    "palpitaciones": "¿Ha sentido palpitaciones o taquicardia?",
    "nausea": "¿Ha tenido náuseas?",
    "nauseas": "¿Ha tenido náuseas?",
    "vomito": "¿Ha tenido vómitos?",
    "vómito": "¿Ha tenido vómitos?",
    "diarrea": "¿Ha tenido diarrea?",
    "escalofrios": "¿Ha tenido escalofríos?",
    "sudoracion": "¿Ha tenido sudoración excesiva?",
    "sudoracion nocturna": "¿Ha tenido sudoración nocturna?",
    "perdida de peso": "¿Ha perdido peso sin razón aparente?",
    "perdida del apetito": "¿Ha perdido el apetito?",
    "mareo": "¿Ha tenido mareos?",
    "vertigo": "¿Ha tenido vértigo?",
    "desmayo": "¿Se ha desmayado?",
    "sincope": "¿Se ha desmayado?",
    "erupcion cutanea": "¿Tiene erupción cutánea?",
    "rash": "¿Tiene erupción cutánea?",
    "picazon": "¿Tiene picazón en alguna parte del cuerpo?",
    "prurito": "¿Tiene picazón en alguna parte del cuerpo?",
    "hinchazon": "¿Tiene hinchazón en alguna parte del cuerpo?",
    "edema": "¿Tiene hinchazón en alguna parte del cuerpo?",
    "ictericia": "¿Tiene coloración amarillenta en la piel u ojos?",
    "orina oscura": "¿Tiene orina oscura?",
    "sangrado": "¿Ha tenido sangrado?",
    "moretones": "¿Le salen moretones con facilidad?",
    "fotofobia": "¿Tiene molestia a la luz?",
    "sensibilidad a la luz": "¿Tiene molestia a la luz?",
    "fonofobia": "¿Tiene molestia a los ruidos fuertes?",
}


def _build_specific_question(symptom_name: str) -> str | None:
    key = symptom_name.lower().strip()
    for pattern, question in _SPECIFIC_QUESTIONS.items():
        if pattern in key or key in pattern:
            return question
    return None


async def generate_followup(
    symptoms: list[str],
    patient_info: dict | None = None,
    excluded_symptoms: list[str] | None = None,
) -> dict:
    """Generate follow-up question based on current symptoms.

    Always tries to ask discriminating questions first.
    Only returns ready=True when the evidence is both sufficient AND
    unambiguous (a strong lead with a healthy gap to the runner-up). While
    any useful discriminating question remains unanswered, the system keeps
    gathering data instead of jumping to a conclusion.

    ``excluded_symptoms`` are symptoms the doctor explicitly stated are NOT
    present; they are used as negative evidence and never re-asked.

    If patient_info is provided, vital signs are merged into the symptom list.

    Returns:
        dict with:
            - question: str (the follow-up question)
            - suggestions: list[str] (symptoms to suggest asking about)
            - diagnoses: list[dict] (current top diagnoses)
            - ready: bool (if evidence is sufficient and unambiguous)
    """
    if patient_info:
        symptoms = merge_vital_symptoms(patient_info, symptoms)

    excluded = [e for e in (excluded_symptoms or []) if e]
    results = await diagnose(
        symptoms,
        patient_info=patient_info,
        excluded_symptoms=excluded,
    )
    if not results:
        return {
            "question": "No encontré enfermedades que coincidan con esos síntomas. ¿Podrías describir mejor los síntomas?",
            "suggestions": [],
            "diagnoses": [],
            "ready": False,
        }

    top = results[:MAX_CANDIDATES_FOR_SUGGESTIONS]
    top_names = {d["disease_name"] for d in top}

    db = get_db()
    if db is None:
        return {"question": "", "suggestions": [], "diagnoses": results, "ready": True}

    disease_docs = await db.diseases.find(
        {"name": {"$in": list(top_names)}}
    ).to_list(length=None)

    # Map disease_name -> set of symptoms
    disease_symptoms_map: dict[str, set[str]] = {}
    for doc in disease_docs:
        name = doc["name"]
        disease_symptoms_map[name] = {
            s.lower().strip() for s in doc.get("symptoms", [])
        }

    already_mentioned = set(s.lower().strip() for s in symptoms)
    already_mentioned.update(e.lower().strip() for e in excluded)

    # --- Coherent question pool --------------------------------------
    # Every question must stay topically anchored to what the doctor is
    # describing. Only candidates that share at least one symptom with the
    # leader may contribute symptoms to ask about, and "exotic" unique
    # symptoms are only asked once the evidence is credible (anchored).
    top_names = {d["disease_name"] for d in top}

    leader = results[0]
    leader_conf = leader.get("confidence", 0)
    leader_name = leader["disease_name"]
    leader_set = disease_symptoms_map.get(leader_name, set())

    def _in_family(d_name: str) -> bool:
        if d_name == leader_name:
            return True
        return bool(disease_symptoms_map.get(d_name, set()) & leader_set)

    family_top = [d for d in results if _in_family(d["disease_name"])][:MAX_CANDIDATES_FOR_SUGGESTIONS]
    family_names = [d["disease_name"] for d in family_top]

    # Until the leader clears the floor we only ask what the candidates
    # have in COMMON (proper descriptors of the reported complaint). That
    # avoids asking "¿el dolor de cabeza es pulsátil?" after a mere "tos".
    anchored = leader_conf >= QUESTION_SOURCE_FLOOR

    shared_conf: dict[str, float] = {}
    for d in family_top:
        conf = d.get("confidence", 0)
        for s in disease_symptoms_map.get(d["disease_name"], set()):
            if s in already_mentioned:
                continue
            shared_conf[s] = shared_conf.get(s, 0.0) + conf

    shared_syms = sorted(
        (s for s, _w in shared_conf.items() if _build_specific_question(s)),
        key=lambda s: -shared_conf[s],
    )

    discriminating: dict[str, list[str]] = {}
    for d_name in family_names:
        ds = disease_symptoms_map.get(d_name, set())
        others = set()
        for other_name in family_names:
            if other_name != d_name:
                others |= disease_symptoms_map.get(other_name, set())
        unique = ds - others - already_mentioned
        if unique:
            discriminating[d_name] = list(unique)

    picks: list[str] = []
    questions_asked: list[str] = []

    def _try_add(sym: str) -> bool:
        """Return True if the symptom was added as a question."""
        nonlocal picks
        if len(picks) >= MAX_FOLLOWUP_SUGGESTIONS:
            return False
        if sym in picks:
            return False
        q = _build_specific_question(sym)
        if q and q not in questions_asked:
            picks.append(sym)
            questions_asked.append(q)
            return True
        return False

    # 1st priority: shared symptoms (breadth of the weak signal first)
    for sym in shared_syms:
        if len(picks) >= MAX_FOLLOWUP_SUGGESTIONS:
            break
        _try_add(sym)

    if anchored:
        # 2nd priority: the leader's most specific missing symptoms
        for sym in leader.get("missing_key_symptoms", []):
            if len(picks) >= MAX_FOLLOWUP_SUGGESTIONS:
                break
            _try_add(sym)

        # 3rd priority: discriminating symptoms across the family
        if len(picks) < MAX_FOLLOWUP_SUGGESTIONS:
            for d_name in family_names:
                for sym in sorted(discriminating.get(d_name, [])):
                    if len(picks) >= MAX_FOLLOWUP_SUGGESTIONS:
                        break
                    _try_add(sym)

        # 4th priority: any remaining unmentioned family symptom
        if len(picks) < MAX_FOLLOWUP_SUGGESTIONS:
            for d_name in family_names:
                for sym in disease_symptoms_map.get(d_name, set()):
                    if len(picks) >= MAX_FOLLOWUP_SUGGESTIONS:
                        break
                    _try_add(sym)

    if not questions_asked:
        # Absolute last resort: any discriminating symptom of the leader.
        for sym in sorted(discriminating.get(leader_name, [])):
            if len(picks) >= MAX_FOLLOWUP_SUGGESTIONS:
                break
            _try_add(sym)

    # --- Determine if ready (strict) ---
    # The AI proposes; it does not decide. "Ready" means "enough evidence to
    # present a differential for the professional to confirm".
    is_ready = False
    if results:
        top_conf = results[0].get("confidence", 0)
        runner_up = results[1].get("confidence", 0) if len(results) > 1 else 0.0
        gap = top_conf - runner_up
        unique_leader = len(results) == 1 or gap >= READY_MIN_GAP

        if unique_leader and top_conf >= READY_MIN_TOP_CONFIDENCE:
            is_ready = True
        elif top_conf >= READY_HIGH_CONFIDENCE and gap >= READY_MIN_GAP:
            is_ready = True

    if is_ready:
        return {
            "question": "",
            "suggestions": [],
            "diagnoses": results,
            "ready": True,
        }

    # --- Build the question text ---
    question = ""
    if questions_asked:
        question = questions_asked[0] + " "
        if len(picks) > 1:
            sym_texts = [_prettify_symptom(p) for p in picks[1:]]
            question += "Además, ¿presenta " + ", ".join(sym_texts) + "?"
        else:
            disease_hints = [d["disease_name"] for d in top[:3]]
            question += f"(Podría ser {' o '.join(disease_hints)})"
    else:
        disease_hints = [d["disease_name"] for d in top[:3]]
        question = (
            f"Basado en lo que me dices, podría ser {' o '.join(disease_hints)}. "
            "¿Podrías darme más detalles sobre los síntomas?"
        )

    return {
        "question": question,
        "suggestions": picks,
        "diagnoses": top,
        "ready": False,
    }
