from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from app.database.mongodb import get_db
from app.auth.permissions import require_roles
from app.rate_limit import limiter
from app.expert_system.engine import diagnose, get_treatment, narrow_diagnoses
from app.expert_system.normalizer import normalize_symptoms, load_learned, load_catalog

router = APIRouter()


class DiagnoseRequest(BaseModel):
    symptoms: list[str]
    excluded_symptoms: list[str] = []


class DiagnoseResponse(BaseModel):
    normalized_symptoms: list[str]
    excluded_symptoms: list[str] = []
    unmatched_symptoms: list[str]
    suggestions: dict
    possible_diagnoses: list[dict]
    total_candidates: int


class TreatmentRequest(BaseModel):
    disease_name: str


class TreatmentResponse(BaseModel):
    disease_name: str
    medicines: list[dict]
    general_recommendations: str


class LearnRequest(BaseModel):
    phrase: str
    canonical_symptom: str


class LearnResponse(BaseModel):
    phrase: str
    canonical_symptom: str
    message: str


async def _load_learned_from_db():
    db = get_db()
    if db is None:
        return
    docs = await db.learned_synonyms.find().to_list(length=None)
    mapping = {doc["phrase"]: doc["canonical_symptom"] for doc in docs}
    load_learned(mapping)

    slice_find = await db.symptoms.find({}, {"name": 1}).to_list(length=None)
    load_catalog([doc.get("name", "") for doc in slice_find])


@router.post("/diagnose", response_model=DiagnoseResponse)
@limiter.limit("30/minute")
async def diagnose_symptoms(
    request: Request,
    data: DiagnoseRequest,
    current_user=Depends(require_roles("medico", "admin", "super_admin")),
):
    if not data.symptoms:
        return DiagnoseResponse(
            normalized_symptoms=[], unmatched_symptoms=[],
            suggestions={}, possible_diagnoses=[], total_candidates=0,
        )

    await _load_learned_from_db()
    result = normalize_symptoms(data.symptoms)
    normalized = result["matched"]

    diagnoses_result = await diagnose(
        normalized,
        excluded_symptoms=data.excluded_symptoms or result.get("negated", []),
    )
    narrow_pool = narrow_diagnoses(diagnoses_result, normalized)
    return DiagnoseResponse(
        normalized_symptoms=normalized,
        excluded_symptoms=data.excluded_symptoms or result.get("negated", []),
        unmatched_symptoms=result["unmatched"],
        suggestions=result["suggestions"],
        possible_diagnoses=narrow_pool,
        total_candidates=len(diagnoses_result),
    )


@router.post("/treatment", response_model=TreatmentResponse | None)
async def recommend_treatment(
    request: TreatmentRequest,
    current_user=Depends(require_roles("medico", "admin", "super_admin")),
):
    treatment = await get_treatment(request.disease_name)
    if not treatment:
        return None
    return TreatmentResponse(
        disease_name=treatment["disease_name"],
        medicines=treatment["medicines"],
        general_recommendations=treatment["general_recommendations"],
    )


@router.post("/learn", response_model=LearnResponse)
async def learn_symptom(
    request: LearnRequest,
    current_user=Depends(require_roles("admin", "super_admin")),
):
    """Teach the system a new phrase → symptom mapping."""
    from app.expert_system.normalizer import normalize

    phrase_norm = normalize(request.phrase)
    if not phrase_norm:
        raise HTTPException(status_code=400, detail="La frase no puede estar vacía")

    canonical = normalize(request.canonical_symptom)
    db = get_db()
    if db is None:
        raise HTTPException(status_code=503, detail="Base de datos no disponible")

    existing = await db.learned_synonyms.find_one({"phrase": phrase_norm})
    if existing:
        await db.learned_synonyms.update_one(
            {"_id": existing["_id"]},
            {"$set": {"canonical_symptom": canonical}},
        )
        msg = f"Updated mapping: '{request.phrase}' → '{canonical}'"
    else:
        await db.learned_synonyms.insert_one({
            "phrase": phrase_norm,
            "canonical_symptom": canonical,
        })
        msg = f"Learned: '{request.phrase}' → '{canonical}'"

    await _load_learned_from_db()
    return LearnResponse(
        phrase=request.phrase,
        canonical_symptom=canonical,
        message=msg,
    )


@router.get("/learned")
async def get_learned(current_user=Depends(require_roles("admin", "super_admin"))):
    """List all custom learned mappings."""
    db = get_db()
    if db is None:
        return []
    docs = await db.learned_synonyms.find().to_list(length=None)
    return [{"phrase": d["phrase"], "canonical_symptom": d["canonical_symptom"]} for d in docs]
