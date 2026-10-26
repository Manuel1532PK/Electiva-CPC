from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from pydantic import BaseModel
from app.database.mongodb import get_db
from app.auth.permissions import require_roles
from app.utils import normalize_text
from bson import ObjectId
from typing import Optional, Any

router = APIRouter()


class SymptomCreate(BaseModel):
    name: str
    description: str | None = None
    category: str | None = None


class SymptomUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None


class DiseaseCreate(BaseModel):
    name: str
    description: str | None = None
    symptoms: list[str] = []
    severity: str = "moderate"


class DiseaseUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    symptoms: Optional[list[str]] = None
    severity: Optional[str] = None


class MedicineItem(BaseModel):
    name: str
    dosage: str | None = None
    frequency: str | None = None
    duration: str | None = None


class TreatmentUpdate(BaseModel):
    disease_name: Optional[str] = None
    medicines: Optional[list[Any]] = None
    general_recommendations: Optional[str] = None
    source: Optional[str] = None


class MedicineCreate(BaseModel):
    name: str
    dosage: str | None = None
    frequency: str | None = None
    duration: str | None = None


class TreatmentCreate(BaseModel):
    disease_name: str
    medicines: list[Any] = []
    general_recommendations: str | None = None
    source: str | None = None


def _symptom_out(s: dict) -> dict:
    return {"id": str(s["_id"]), "name": s["name"], "description": s.get("description"), "category": s.get("category")}


def _disease_out(d: dict) -> dict:
    return {
        "id": str(d["_id"]),
        "name": d["name"],
        "description": d.get("description"),
        "symptoms": d.get("symptoms", []),
        "severity": d.get("severity"),
    }


def _treatment_out(t: dict) -> dict:
    return {
        "id": str(t["_id"]),
        "disease_name": t["disease_name"],
        "medicines": t.get("medicines", []),
        "general_recommendations": t.get("general_recommendations"),
        "source": t.get("source"),
    }


def _non_empty(data: dict) -> dict:
    return {k: v for k, v in data.items() if v is not None and v != ""}


# ── Symptoms ─────────────────────────────────────────────────────

@router.post("/symptoms")
async def create_symptom(
    data: SymptomCreate,
    current_user=Depends(require_roles("admin", "super_admin")),
):
    db = get_db()
    name = normalize_text(data.name)
    if not name:
        raise HTTPException(status_code=422, detail="Nombre inválido")
    existing = await db.symptoms.find_one({"name": name})
    if existing:
        raise HTTPException(status_code=409, detail="El síntoma ya existe")
    result = await db.symptoms.insert_one({"name": name, "description": data.description, "category": data.category})
    return {"id": str(result.inserted_id), "name": name}


@router.get("/symptoms")
async def list_symptoms(current_user=Depends(require_roles("medico", "admin", "super_admin"))):
    db = get_db()
    symptoms = await db.symptoms.find().to_list(length=None)
    return [_symptom_out(s) for s in symptoms]


@router.put("/symptoms/{symptom_id}")
async def update_symptom(
    symptom_id: str,
    data: SymptomUpdate,
    current_user=Depends(require_roles("admin", "super_admin")),
):
    db = get_db()
    update = _non_empty(data.model_dump())
    if not update:
        raise HTTPException(status_code=400, detail="Nada que actualizar")
    if "name" in update:
        update["name"] = normalize_text(update["name"])
        dup = await db.symptoms.find_one({"name": update["name"], "_id": {"$ne": ObjectId(symptom_id)}})
        if dup:
            raise HTTPException(status_code=409, detail="Otro síntoma ya usa ese nombre")
    res = await db.symptoms.update_one({"_id": ObjectId(symptom_id)}, {"$set": update})
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Síntoma no encontrado")
    doc = await db.symptoms.find_one({"_id": ObjectId(symptom_id)})
    return _symptom_out(doc)


@router.delete("/symptoms/{symptom_id}")
async def delete_symptom(
    symptom_id: str,
    current_user=Depends(require_roles("admin", "super_admin")),
):
    db = get_db()
    res = await db.symptoms.delete_one({"_id": ObjectId(symptom_id)})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Síntoma no encontrado")
    return {"deleted": True, "id": symptom_id}


# ── Diseases ─────────────────────────────────────────────────────

@router.post("/diseases")
async def create_disease(
    data: DiseaseCreate,
    current_user=Depends(require_roles("admin", "super_admin")),
):
    db = get_db()
    name = normalize_text(data.name)
    if not name:
        raise HTTPException(status_code=422, detail="Nombre inválido")
    existing = await db.diseases.find_one({"name": name})
    if existing:
        raise HTTPException(status_code=409, detail="La enfermedad ya existe")
    result = await db.diseases.insert_one({"name": name, "description": data.description, "symptoms": [normalize_text(s) for s in data.symptoms if normalize_text(s)], "severity": data.severity})
    return {"id": str(result.inserted_id), "name": name}


@router.get("/diseases")
async def list_diseases(current_user=Depends(require_roles("medico", "admin", "super_admin"))):
    db = get_db()
    diseases = await db.diseases.find().to_list(length=None)
    return [_disease_out(d) for d in diseases]


@router.put("/diseases/{disease_id}")
async def update_disease(
    disease_id: str,
    data: DiseaseUpdate,
    current_user=Depends(require_roles("admin", "super_admin")),
):
    db = get_db()
    update = _non_empty(data.model_dump())
    if not update:
        raise HTTPException(status_code=400, detail="Nada que actualizar")
    if update.get("name"):
        update["name"] = normalize_text(update["name"])
        dup = await db.diseases.find_one({"name": update["name"], "_id": {"$ne": ObjectId(disease_id)}})
        if dup:
            raise HTTPException(status_code=409, detail="Otra enfermedad ya usa ese nombre")
    if update.get("symptoms"):
        update["symptoms"] = list({normalize_text(s) for s in update["symptoms"] if normalize_text(s)})
    res = await db.diseases.update_one({"_id": ObjectId(disease_id)}, {"$set": update})
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Enfermedad no encontrada")
    doc = await db.diseases.find_one({"_id": ObjectId(disease_id)})
    return _disease_out(doc)


@router.delete("/diseases/{disease_id}")
async def delete_disease(
    disease_id: str,
    current_user=Depends(require_roles("admin", "super_admin")),
):
    db = get_db()
    res = await db.diseases.delete_one({"_id": ObjectId(disease_id)})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Enfermedad no encontrada")
    return {"deleted": True, "id": disease_id}


# ── Treatments ───────────────────────────────────────────────────

@router.post("/treatments")
async def create_treatment(
    data: TreatmentCreate,
    current_user=Depends(require_roles("admin", "super_admin")),
):
    db = get_db()
    disease_name = normalize_text(data.disease_name)
    if not disease_name:
        raise HTTPException(status_code=422, detail="Disease name inválido")
    existing = await db.treatments.find_one({"disease_name": disease_name})
    if existing:
        raise HTTPException(status_code=409, detail="Ya existe un tratamiento para esta enfermedad")
    result = await db.treatments.insert_one({"disease_name": disease_name, "medicines": data.medicines, "general_recommendations": data.general_recommendations, "source": data.source})
    return {"id": str(result.inserted_id), "disease_name": disease_name}


@router.get("/treatments")
async def list_treatments(current_user=Depends(require_roles("medico", "admin", "super_admin"))):
    db = get_db()
    treatments = await db.treatments.find().to_list(length=None)
    return [_treatment_out(t) for t in treatments]


@router.put("/treatments/{treatment_id}")
async def update_treatment(
    treatment_id: str,
    data: TreatmentUpdate,
    current_user=Depends(require_roles("admin", "super_admin")),
):
    db = get_db()
    update = _non_empty(data.model_dump())
    if not update:
        raise HTTPException(status_code=400, detail="Nada que actualizar")
    if update.get("disease_name"):
        update["disease_name"] = normalize_text(update["disease_name"])
        dup = await db.treatments.find_one({"disease_name": update["disease_name"], "_id": {"$ne": ObjectId(treatment_id)}})
        if dup:
            raise HTTPException(status_code=409, detail="Ya existe otro tratamiento para esa enfermedad")
    res = await db.treatments.update_one({"_id": ObjectId(treatment_id)}, {"$set": update})
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Tratamiento no encontrado")
    doc = await db.treatments.find_one({"_id": ObjectId(treatment_id)})
    return _treatment_out(doc)


@router.delete("/treatments/{treatment_id}")
async def delete_treatment(
    treatment_id: str,
    current_user=Depends(require_roles("admin", "super_admin")),
):
    db = get_db()
    res = await db.treatments.delete_one({"_id": ObjectId(treatment_id)})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Tratamiento no encontrado")
    return {"deleted": True, "id": treatment_id}


# ── Bulk import (ingreso masivo) ─────────────────────────────────

VALID_COLLECTIONS = ("symptoms", "diseases", "treatments")

KEY_FIELD = {
    "symptoms": "name",
    "diseases": "name",
    "treatments": "disease_name",
}


async def _upsert_docs(coll, key_field: str, docs: list[dict]) -> dict:
    """Upsert idempotente y normalizado de documentos por clave.

    Devuelve conteos de insertados/actualizados y errores por documento.
    """
    from pymongo.errors import DuplicateKeyError

    inserted = 0
    updated = 0
    errores = []
    for i, doc in enumerate(docs):
        key = normalize_text(doc.get(key_field) or "")
        if not key:
            errores.append({"index": i, "reason": "missing key field"})
            continue
        patch = {k: v for k, v in doc.items() if k != "_id"}
        patch[key_field] = key
        try:
            res = await coll.update_one({key_field: key}, {"$set": patch}, upsert=True)
        except DuplicateKeyError:
            errores.append({"index": i, "reason": "duplicate key (posible colisión con acentos previos)"})
            continue
        if res.upserted_id is not None:
            inserted += 1
        else:
            updated += 1
    return {"inserted": inserted, "updated": updated, "errors": errores}


class BulkImport(BaseModel):
    collection: str  # symptoms | diseases | treatments
    documents: list[dict]
    key_field: str = "name"


@router.post("/bulk")
async def bulk_import(
    data: BulkImport,
    current_user=Depends(require_roles("super_admin")),
):
    db = get_db()
    if data.collection not in VALID_COLLECTIONS:
        raise HTTPException(status_code=400, detail="La colección debe ser symptoms, diseases o treatments")
    coll = db[data.collection]
    result = await _upsert_docs(coll, data.key_field, data.documents)
    return {"inserted": result["inserted"], "updated": result["updated"], "errors": result["errors"]}


# ── Importación por archivo (CSV / Excel / JSON) ─────────────────
# Disponible exclusivamente para super_admin.

def _clean_field_name(name: str) -> str:
    """Normaliza nombres de columna (minúsculas, sin acentos/espacios)."""
    n = normalize_text(name)
    return n.replace(" ", "_").replace("-", "_")


def _split_list(value: Any) -> list[str]:
    """Convierte un valor en lista de strings normalizados (separa por | o ,)."""
    if value is None:
        return []
    if isinstance(value, list):
        items = value
    else:
        text = str(value)
        items = [p for p in text.replace(",", "|").split("|") if p.strip()]
    seen = set()
    out = []
    for it in items:
        n = normalize_text(it)
        if n and n not in seen:
            seen.add(n)
            out.append(n)
    return out


def _parse_json_docs(raw, collection: str) -> list[dict]:
    """Extrae documentos desde JSON: dict completo o array de una colección."""
    if isinstance(raw, list):
        return raw
    if isinstance(raw, dict):
        if collection in raw and isinstance(raw[collection], list):
            return raw[collection]
        # Objeto único
        return [raw]
    raise HTTPException(status_code=400, detail="JSON no reconocido: debe ser un array o un objeto con la colección")


def _parse_tabular_docs(rows: list[dict], collection: str) -> dict:
    """Convierte filas tabulares en documentos para la colección indicada."""
    mapped: list[dict] = []
    for i, row in enumerate(rows):
        clean = {_clean_field_name(k): v for k, v in row.items() if k is not None}
        doc = None
        if collection == "symptoms":
            if clean.get("name"):
                doc = {
                    "name": str(clean["name"]),
                    "description": str(clean.get("description") or ""),
                    "category": str(clean.get("category") or "generales"),
                }
        elif collection == "diseases":
            if clean.get("name"):
                doc = {
                    "name": str(clean["name"]),
                    "description": str(clean.get("description") or ""),
                    "severity": str(clean.get("severity") or "moderate"),
                    "symptoms": _split_list(clean.get("symptoms")),
                }
        else:  # treatments
            key = clean.get("disease_name") or clean.get("diseasename") or clean.get("name")
            if key:
                doc = {
                    "disease_name": str(key),
                    "general_recommendations": str(clean.get("general_recommendations") or clean.get("generalrecommendations") or ""),
                    "medicines": [],
                    "alternative_medicines": [],
                    "non_pharmacological_treatments": _split_list(clean.get("non_pharmacological_treatments") or clean.get("nonpharmacologicaltreatments")),
                }
        if doc is not None:
            mapped.append(doc)
    return {"docs": mapped}


@router.post("/import-file")
async def import_file(
    file: UploadFile = File(...),
    collection: str = Form(...),
    current_user=Depends(require_roles("super_admin")),
):
    """Importa síntomas, enfermedades o tratamientos desde CSV, Excel o JSON.

    El archivo (multipart) se parsea según su extensión y se inserta/actualiza
    de forma idempotente en la colección indicada, normalizando las claves.
    """
    if collection not in VALID_COLLECTIONS:
        raise HTTPException(status_code=400, detail="La colección debe ser symptoms, diseases o treatments")

    raw = await file.read()
    if not raw:
        raise HTTPException(status_code=400, detail="El archivo está vacío")

    filename = (file.filename or "").lower()
    ext = filename.rsplit(".", 1)[-1] if "." in filename else ""

    docs: list[dict] = []

    if ext == "json":
        import json as _json
        try:
            data = _json.loads(raw.decode("utf-8"))
        except Exception:
            raise HTTPException(status_code=400, detail="JSON inválido")
        docs = _parse_json_docs(data, collection)
    elif ext in ("csv", "txt"):
        import csv as _csv
        import io as _io
        text = raw.decode("utf-8-sig", errors="replace")
        reader = _csv.DictReader(_io.StringIO(text))
        rows = list(reader)
        docs = _parse_tabular_docs(rows, collection)["docs"]
    elif ext in ("xlsx", "xls"):
        import io as _io
        try:
            import pandas as pd
        except ImportError:
            raise HTTPException(status_code=400, detail="pandas no está instalado en el servidor para leer Excel")
        try:
            df = pd.read_excel(_io.BytesIO(raw)).fillna("").astype(str)
            rows = df.to_dict("records")
        except Exception:
            raise HTTPException(status_code=400, detail="No se pudo leer el archivo Excel")
        docs = _parse_tabular_docs(rows, collection)["docs"]
    else:
        raise HTTPException(status_code=400, detail=f"Formato no soportado: {ext or 'desconocido'}. Usa .json, .csv o .xlsx")

    if not docs:
        raise HTTPException(status_code=422, detail="No se encontraron documentos válidos en el archivo")

    db = get_db()
    coll = db[collection]
    result = await _upsert_docs(coll, KEY_FIELD[collection], docs)
    return {
        "collection": collection,
        "file": filename,
        "detected": len(docs),
        "inserted": result["inserted"],
        "updated": result["updated"],
        "errors": result["errors"],
    }


# ── Integridad ───────────────────────────────────────────────────

@router.get("/integrity")
async def integrity_check(current_user=Depends(require_roles("medico", "admin", "super_admin"))):
    db = get_db()
    report = {"missing_symptoms": [], "treatments_without_disease": [], "diseases_without_treatment": []}

    all_symptoms = await db.symptoms.find({}, {"name": 1}).to_list(length=None)
    sym_names = {s["name"].lower().strip() for s in all_symptoms}

    diseases = await db.diseases.find({}).to_list(length=None)
    disease_names = {d["name"].lower().strip() for d in diseases}

    for d in diseases:
        for sym in d.get("symptoms", []):
            if sym.lower().strip() not in sym_names:
                report["missing_symptoms"].append({"disease": d["name"], "symptom": sym})

    treatments = await db.treatments.find({}, {"disease_name": 1}).to_list(length=None)
    treatment_names = {t["disease_name"].lower().strip() for t in treatments}

    for t in treatments:
        if t["disease_name"].lower().strip() not in disease_names:
            report["treatments_without_disease"].append(t["disease_name"])

    for dn in disease_names:
        if dn not in treatment_names:
            report["diseases_without_treatment"].append(dn)

    return report
