from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.auth.permissions import require_roles
from app.expert_system.normalizer import (
    normalize_symptoms, is_thank_you,
    pick_response, pick_unknown_response,
    pick_report_transition, find_negated_symptoms,
    classify_conversation,
)
from app.expert_system.conversation import generate_followup
from app.database.mongodb import get_db
from app.expert_system.engine import get_treatment, recommend_treatment, merge_vital_symptoms, narrow_diagnoses

router = APIRouter()


class ConverseRequest(BaseModel):
    message: str
    current_symptoms: list[str] = []
    excluded_symptoms: list[str] = []
    patient_info: dict = {}


class ConverseResponse(BaseModel):
    reply: str
    normalized_symptoms: list[str] = []
    excluded_symptoms: list[str] = []
    suggestions: list[str] = []
    diagnoses: list[dict] = []
    treatment: dict | None = None
    ready: bool = False
    greeting: bool = False


def _merge_unique(base: list[str], extra: list[str]) -> list[str]:
    seen = set(base)
    out = list(base)
    for item in extra:
        key = item.strip().lower()
        if key and key not in seen and key not in {x.strip().lower() for x in out}:
            out.append(item)
            seen.add(key)
    return out


@router.post("/converse", response_model=ConverseResponse)
async def converse(
    request: ConverseRequest,
    current_user=Depends(require_roles("medico", "admin", "super_admin")),
):
    try:
        msg = request.message.strip()
        already_has_symptoms = len(request.current_symptoms) > 0

        # ── 1. Conversational layer ────────────────────────────
        category = classify_conversation(msg)

        if category == "greeting" and not already_has_symptoms:
            return ConverseResponse(reply=pick_response("greeting"), greeting=True)

        if category == "how_are_you":
            return ConverseResponse(reply=pick_response("how_are_you"), greeting=True)

        if category in ("mood_negative", "mood_positive"):
            return ConverseResponse(reply=pick_response(category), greeting=True)

        if category == "goodbye":
            if already_has_symptoms:
                trans = pick_report_transition()
                return ConverseResponse(
                    reply=f"{pick_response('goodbye')} {trans}",
                    normalized_symptoms=request.current_symptoms,
                    greeting=True,
                )
            return ConverseResponse(reply=pick_response("goodbye"), greeting=True)

        if category == "ready_report":
            if already_has_symptoms:
                from app.expert_system.engine import diagnose as diag_engine
                all_diags = await diag_engine(
                    request.current_symptoms,
                    patient_info=request.patient_info,
                    excluded_symptoms=request.excluded_symptoms,
                )
                all_diags = narrow_diagnoses(all_diags, request.current_symptoms)
                if all_diags:
                    lines = [f"- {d['disease_name']} ({d['confidence']:.0%})" for d in all_diags[:3]]
                    reply = (
                        f"Resumen del diagnóstico (propuesta para confirmación):\n\n"
                        f"Síntomas registrados: {', '.join(request.current_symptoms)}\n"
                        + (f"\nSíntomas descartados: {', '.join(request.excluded_symptoms)}" if request.excluded_symptoms else "")
                        + "\n\nPosibles diagnósticos:\n" + "\n".join(lines) +
                        "\n\nRevisa, confirma o descarta cada uno. Puedes pedirme el tratamiento escribiendo su nombre."
                    )
                    return ConverseResponse(
                        reply=reply,
                        normalized_symptoms=request.current_symptoms,
                        excluded_symptoms=request.excluded_symptoms,
                        diagnoses=all_diags,
                        ready=True,
                    )
            return ConverseResponse(
                reply="Todavía no hay suficiente evidencia para proponer diagnósticos. Describe más síntomas primero.",
                greeting=True,
            )

        if is_thank_you(msg):
            if already_has_symptoms:
                trans = pick_report_transition()
                return ConverseResponse(
                    reply=f"De nada. {trans}",
                    normalized_symptoms=request.current_symptoms,
                    excluded_symptoms=request.excluded_symptoms,
                )
            return ConverseResponse(reply="De nada. ¿Necesitas ayuda con algún diagnóstico?")

        if category in ("what_is", "chatty", "encouragement"):
            return ConverseResponse(reply=pick_response(category), greeting=True)

        # ── 2. 🚨 Try treatment lookup FIRST (before normalizer) ──────
        # The normalizer intercepts disease names like "Migraña", "Amigdalitis",
        # "Cólico Nefrítico", etc. because they are substrings of symptom synonyms.
        # We must check for treatment before symptom matching so clicking on a
        # diagnosis card actually returns the treatment instead of re-running the diagnosis.
        # Substring guessing that could send a symptom like "tos" to an unrelated
        # treatment is prevented inside get_treatment() (word-boundary matching).
        if already_has_symptoms:
            treatment = await recommend_treatment(msg.strip(), request.patient_info)
            if not treatment or not treatment.get("available"):
                treatment = await get_treatment(msg.strip())
            if treatment:
                return ConverseResponse(
                    reply=f"Tratamiento para {treatment.get('disease_name', '')}:",
                    normalized_symptoms=request.current_symptoms,
                    excluded_symptoms=request.excluded_symptoms,
                    treatment=treatment,
                    ready=True,
                )

        # ── 3. Load learned synonyms + Atlas catalog ──────────
        from app.expert_system.normalizer import load_learned, load_catalog
        db = get_db()
        if db is not None:
            docs = await db.learned_synonyms.find().to_list(length=None)
            mapping = {doc["phrase"]: doc["canonical_symptom"] for doc in docs}
            load_learned(mapping)

            # Build the catalog of symptoms currently in MongoDB Atlas so the
            # matcher only captures symptoms that are actually loaded in the DB.
            slice_find = await db.symptoms.find({}, {"name": 1}).to_list(length=None)
            load_catalog([doc.get("name", "") for doc in slice_find])

        # ── 4. Process as symptom ───────────────────────────────
        result = normalize_symptoms([msg])
        negated_this_msg = result.get("negated", []) or find_negated_symptoms(msg)
        all_symptoms = request.current_symptoms.copy()
        all_symptoms = merge_vital_symptoms(request.patient_info, all_symptoms)
        excluded = _merge_unique(request.excluded_symptoms, negated_this_msg)
        excl_keys = {x.strip().lower() for x in excluded}

        for s in result["matched"]:
            # A symptom the doctor just denied is NOT present.
            if s.strip().lower() in excl_keys or s in negated_this_msg:
                continue
            if s not in all_symptoms:
                all_symptoms.append(s)

        # A symptom previously excluded must not remain as present either.
        all_symptoms = [s for s in all_symptoms if s.strip().lower() not in excl_keys]

        # Nothing matched (treatment check already happened above)
        if not result["matched"]:
            if result["suggestions"]:
                key = next(iter(result["suggestions"]))
                sug_list = result["suggestions"][key]
                if sug_list:
                    return ConverseResponse(
                        reply=f"No reconozco exactamente ese síntoma. ¿Podría ser '{sug_list[0]}'?",
                        suggestions=sug_list,
                        normalized_symptoms=all_symptoms,
                        excluded_symptoms=excluded,
                        greeting=True,
                    )

            # If user already had symptoms, just say unknown kindly
            if already_has_symptoms:
                reply = f"No entendí bien '{msg}' como síntoma. Describe los síntomas de otra forma o dime 'listo' para el informe."
                if negated_this_msg:
                    reply = f"Entendido: descarto {', '.join(negated_this_msg)}."
                return ConverseResponse(
                    reply=reply,
                    normalized_symptoms=all_symptoms,
                    excluded_symptoms=excluded,
                )

            return ConverseResponse(reply=pick_unknown_response(), greeting=True)

        # ── 4. Symptoms recognized ─────────────────────────────
        followup = await generate_followup(all_symptoms, request.patient_info, excluded)
        followup["diagnoses"] = narrow_diagnoses(followup["diagnoses"], all_symptoms)

        if followup["ready"]:
            diag_list = [
                f"- {d['disease_name']} ({d['confidence']:.0%}, {d['matched_symptoms']} síntomas)"
                for d in followup["diagnoses"]
            ]
            reply = (
                "He reunido suficiente evidencia. Propuesta de diagnósticos diferenciales "
                "(revisa y confirma cuál corresponde):\n"
                + "\n".join(diag_list)
                + "\n\nEscribe el nombre del diagnóstico para ver el tratamiento."
            )
            return ConverseResponse(
                reply=reply,
                normalized_symptoms=all_symptoms,
                excluded_symptoms=excluded,
                diagnoses=followup["diagnoses"],
                ready=True,
            )

        # Build reply with transition hint
        trans = pick_report_transition()
        reply = followup["question"] + "\n\n" + trans
        return ConverseResponse(
            reply=reply,
            normalized_symptoms=all_symptoms,
            excluded_symptoms=excluded,
            suggestions=followup["suggestions"],
            diagnoses=followup["diagnoses"],
            ready=False,
        )

    except Exception as e:
        import traceback
        print("ERROR in converse:", str(e), traceback.format_exc())
        return ConverseResponse(
            reply=f"Error interno: {str(e)}",
            greeting=True,
        )
