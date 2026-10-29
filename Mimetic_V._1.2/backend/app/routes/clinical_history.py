from fastapi import APIRouter, HTTPException, status, Depends, Query
from datetime import datetime
from bson import ObjectId
from typing import Optional
from app.database.mongodb import get_db
from app.auth.dependencies import get_current_user
from app.auth.permissions import require_roles
from app.models.user import UserOut
from app.models.clinical_history import (
    ClinicalHistoryCreate,
    ClinicalHistoryOut,
    SessionCreate,
    SessionUpdate,
    SessionOut,
    SearchResultItem,
)

router = APIRouter()


def history_to_out(hist: dict) -> ClinicalHistoryOut:
    return ClinicalHistoryOut(
        id=str(hist["_id"]),
        document_number=hist.get("document_number", ""),
        document_type=hist.get("document_type", ""),
        first_name=hist.get("first_name", ""),
        last_name=hist.get("last_name", ""),
        birth_date=hist.get("birth_date", ""),
        age=hist.get("age", ""),
        gender=hist.get("gender", ""),
        occupation=hist.get("occupation", ""),
        phone=hist.get("phone", ""),
        country=hist.get("country", ""),
        department=hist.get("department", ""),
        city=hist.get("city", ""),
        created_at=hist.get("created_at", datetime.utcnow()),
        updated_at=hist.get("updated_at", datetime.utcnow()),
    )


def session_to_out(s: dict) -> SessionOut:
    return SessionOut(
        id=str(s["_id"]),
        document_number=s.get("document_number", ""),
        doctor_id=s.get("doctor_id", ""),
        doctor_name=s.get("doctor_name", ""),
        hospital_id=s.get("hospital_id", ""),
        hospital_name=s.get("hospital_name", ""),
        date=s.get("date", datetime.utcnow()),
        consultation_reason=s.get("consultation_reason", ""),
        symptom_evolution=s.get("symptom_evolution", ""),
        tobacco=s.get("tobacco", ""),
        alcohol=s.get("alcohol", ""),
        substances=s.get("substances", ""),
        physical_activity=s.get("physical_activity", ""),
        pregnancy=s.get("pregnancy", ""),
        medical_history=s.get("medical_history", ""),
        surgical_history=s.get("surgical_history", ""),
        pharmacological_history=s.get("pharmacological_history", ""),
        allergies=s.get("allergies", ""),
        blood_pressure=s.get("blood_pressure", ""),
        heart_rate=s.get("heart_rate", ""),
        respiratory_rate=s.get("respiratory_rate", ""),
        temperature=s.get("temperature", ""),
        oxygen_saturation=s.get("oxygen_saturation", ""),
        weight=s.get("weight", ""),
        height=s.get("height", ""),
        triage_level=s.get("triage_level", 0) or 0,
        triage_system=s.get("triage_system", ""),
        triage_discriminators=s.get("triage_discriminators", ""),
        triage_score=s.get("triage_score", ""),
        labs=s.get("labs", {}) or {},
        symptoms=s.get("symptoms", []),
        diagnoses=s.get("diagnoses", []),
        treatment=s.get("treatment"),
        report_html=s.get("report_html", ""),
        doctor_review=s.get("doctor_review"),
    )


# ── Search ───────────────────────────────────────────────────────

@router.get("/clinical-history/search")
async def search_patients(
    q: str = Query("", min_length=0, max_length=50),
    current_user: UserOut = Depends(require_roles("medico", "admin", "super_admin")),
):
    db = get_db()
    if not q or db is None:
        return []

    regex = f"^{q}"

    # Search clinical_histories
    hist_cursor = (
        db.clinical_histories.find(
            {"document_number": {"$regex": regex}},
            {"first_name": 1, "last_name": 1, "document_number": 1, "document_type": 1,
             "birth_date": 1, "age": 1, "gender": 1, "phone": 1, "country": 1,
             "department": 1, "city": 1},
        )
        .sort("document_number", 1)
        .limit(10)
    )
    histories = await hist_cursor.to_list(length=10)
    hist_by_doc = {h["document_number"]: h for h in histories}

    # Search users
    user_cursor = (
        db.users.find(
            {"document_number": {"$regex": regex}},
            {"first_name": 1, "last_name": 1, "document_number": 1, "document_type": 1,
             "birth_date": 1, "phone": 1, "country": 1, "department": 1, "city": 1},
        )
        .sort("document_number", 1)
        .limit(10)
    )
    users = await user_cursor.to_list(length=10)

    # Merge results by document_number
    merged: dict[str, SearchResultItem] = {}

    for h in histories:
        doc = h["document_number"]
        merged[doc] = SearchResultItem(
            document_number=doc,
            first_name=h.get("first_name", ""),
            last_name=h.get("last_name", ""),
            document_type=h.get("document_type", ""),
            source="clinical_history",
            has_clinical_history=True,
            has_user_account=False,
            base_data={
                "first_name": h.get("first_name", ""),
                "last_name": h.get("last_name", ""),
                "document_type": h.get("document_type", ""),
                "birth_date": h.get("birth_date", ""),
                "age": h.get("age", ""),
                "gender": h.get("gender", ""),
                "phone": h.get("phone", ""),
                "country": h.get("country", ""),
                "department": h.get("department", ""),
                "city": h.get("city", ""),
            },
        )

    for u in users:
        doc = u["document_number"]
        if doc in merged:
            item = merged[doc]
            item.source = "both"
            item.has_user_account = True
            # Fill in missing base_data from user if not already present
            bd = item.base_data
            if not bd.get("first_name"):
                bd["first_name"] = u.get("first_name", u.get("name", ""))
            if not bd.get("last_name"):
                bd["last_name"] = u.get("last_name", "")
            if not bd.get("phone"):
                bd["phone"] = u.get("phone", "")
            if not bd.get("country"):
                bd["country"] = u.get("country", "")
            if not bd.get("department"):
                bd["department"] = u.get("department", "")
            if not bd.get("city"):
                bd["city"] = u.get("city", "")
        else:
            merged[doc] = SearchResultItem(
                document_number=doc,
                first_name=u.get("first_name", u.get("name", "")),
                last_name=u.get("last_name", ""),
                document_type=u.get("document_type", ""),
                source="user",
                has_clinical_history=False,
                has_user_account=True,
                base_data={
                    "first_name": u.get("first_name", u.get("name", "")),
                    "last_name": u.get("last_name", ""),
                    "document_type": u.get("document_type", ""),
                    "birth_date": u.get("birth_date", ""),
                    "phone": u.get("phone", ""),
                    "country": u.get("country", ""),
                    "department": u.get("department", ""),
                    "city": u.get("city", ""),
                },
            )

    results = list(merged.values())
    results.sort(key=lambda r: r.document_number)
    return results


# ── Recent patients (landing del historial) ──────────────────────

@router.get("/clinical-history/recent")
async def recent_patients(
    current_user: UserOut = Depends(require_roles("medico", "admin", "super_admin")),
):
    """Pacientes con atenciones registradas, ordenados por actividad reciente."""
    db = get_db()
    if db is None:
        raise HTTPException(status_code=503, detail="Base de datos no disponible")

    cursor = db.sessions.aggregate(
        [
            {"$sort": {"date": -1}},
            {
                "$group": {
                    "_id": "$document_number",
                    "session_count": {"$sum": 1},
                    "last_session_date": {"$first": "$date"},
                    "last_reason": {"$first": "$consultation_reason"},
                    "last_doctor": {"$first": "$doctor_name"},
                    "documents": {
                        "$sum": {
                            "$cond": [
                                {
                                    "$gt": [
                                        {"$strLenCP": {"$ifNull": ["$report_html", ""]}},
                                        0,
                                    ]
                                },
                                1,
                                0,
                            ]
                        }
                    },
                }
            },
            {"$sort": {"last_session_date": -1}},
            {"$limit": 12},
        ]
    )
    rows = await cursor.to_list(length=12)
    documents = [row["_id"] for row in rows if row.get("_id")]
    if not documents:
        return []

    histories = await db.clinical_histories.find(
        {"document_number": {"$in": documents}}
    ).to_list(length=len(documents))
    by_document = {h["document_number"]: h for h in histories}

    return [
        {
            "document_number": row["_id"],
            "first_name": by_document.get(row["_id"], {}).get("first_name", ""),
            "last_name": by_document.get(row["_id"], {}).get("last_name", ""),
            "age": by_document.get(row["_id"], {}).get("age", ""),
            "gender": by_document.get(row["_id"], {}).get("gender", ""),
            "session_count": row.get("session_count", 0),
            "documents": row.get("documents", 0),
            "last_session_date": row.get("last_session_date"),
            "last_reason": row.get("last_reason", ""),
            "last_doctor": row.get("last_doctor", ""),
        }
        for row in rows
    ]


# ── Get clinical history by document ─────────────────────────────

@router.get("/clinical-history/{document}")
async def get_clinical_history(
    document: str,
    current_user: UserOut = Depends(require_roles("medico", "admin", "super_admin")),
):
    db = get_db()
    if db is None:
        raise HTTPException(status_code=503, detail="Base de datos no disponible")

    hist = await db.clinical_histories.find_one({"document_number": document})
    if not hist:
        raise HTTPException(status_code=404, detail="Historia clínica no encontrada")

    return history_to_out(hist)


# ── Create clinical history ──────────────────────────────────────

@router.post("/clinical-history", status_code=status.HTTP_201_CREATED)
async def create_clinical_history(
    data: ClinicalHistoryCreate,
    current_user: UserOut = Depends(require_roles("medico", "admin", "super_admin")),
):
    db = get_db()
    if db is None:
        raise HTTPException(status_code=503, detail="Base de datos no disponible")

    if not data.document_number:
        raise HTTPException(status_code=400, detail="El número de documento es obligatorio")

    existing = await db.clinical_histories.find_one({"document_number": data.document_number})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A clinical history already exists for this document number",
        )

    now = datetime.utcnow()
    doc = {
        "document_number": data.document_number,
        "document_type": data.document_type,
        "first_name": data.first_name,
        "last_name": data.last_name,
        "birth_date": data.birth_date,
        "age": data.age,
        "gender": data.gender,
        "occupation": data.occupation,
        "phone": data.phone,
        "country": data.country,
        "department": data.department,
        "city": data.city,
        "created_at": now,
        "updated_at": now,
    }

    result = await db.clinical_histories.insert_one(doc)
    created = await db.clinical_histories.find_one({"_id": result.inserted_id})
    if created:
        created["_id"] = str(created["_id"])
    return history_to_out(created)


# ── List sessions for a document ─────────────────────────────────

@router.get("/clinical-history/{document}/sessions")
async def list_sessions(
    document: str,
    current_user: UserOut = Depends(require_roles("medico", "admin", "super_admin")),
):
    db = get_db()
    if db is None:
        raise HTTPException(status_code=503, detail="Base de datos no disponible")

    cursor = (
        db.sessions.find({"document_number": document})
        .sort("date", -1)
    )
    sessions = await cursor.to_list(length=100)
    return [session_to_out(s) for s in sessions]


# ── Create session ───────────────────────────────────────────────

@router.post("/clinical-history/{document}/sessions", status_code=status.HTTP_201_CREATED)
async def create_session(
    document: str,
    data: SessionCreate,
    current_user: UserOut = Depends(require_roles("medico", "admin", "super_admin")),
):
    db = get_db()
    if db is None:
        raise HTTPException(status_code=503, detail="Base de datos no disponible")

    # Optionally update the clinical_history updated_at timestamp
    await db.clinical_histories.update_one(
        {"document_number": document},
        {"$set": {"updated_at": datetime.utcnow()}},
    )

    now = datetime.utcnow()
    session_doc = {
        "document_number": document,
        "doctor_id": current_user.id,
        "doctor_name": current_user.name,
        "hospital_id": current_user.hospital_id,
        "hospital_name": "",
        "date": now,
        "consultation_reason": data.consultation_reason,
        "symptom_evolution": data.symptom_evolution,
        "tobacco": data.tobacco,
        "alcohol": data.alcohol,
        "substances": data.substances,
        "physical_activity": data.physical_activity,
        "pregnancy": data.pregnancy,
        "medical_history": data.medical_history,
        "surgical_history": data.surgical_history,
        "pharmacological_history": data.pharmacological_history,
        "allergies": data.allergies,
        "blood_pressure": data.blood_pressure,
        "heart_rate": data.heart_rate,
        "respiratory_rate": data.respiratory_rate,
        "temperature": data.temperature,
        "oxygen_saturation": data.oxygen_saturation,
        "weight": data.weight,
        "height": data.height,
        "triage_level": data.triage_level,
        "triage_system": data.triage_system,
        "triage_discriminators": data.triage_discriminators,
        "triage_score": data.triage_score,
        "labs": data.labs,
        "symptoms": [],
        "diagnoses": [],
        "treatment": None,
        "report_html": "",
    }

    # Resolve hospital name from hospital_id
    if current_user.hospital_id:
        hospital = await db.hospitals.find_one({"_id": ObjectId(current_user.hospital_id)})
        if hospital:
            session_doc["hospital_name"] = hospital.get("name", "")

    result = await db.sessions.insert_one(session_doc)
    created = await db.sessions.find_one({"_id": result.inserted_id})
    return session_to_out(created)


# ── Update session (with diagnosis results) ──────────────────────

@router.put("/clinical-history/{document}/sessions/{session_id}")
async def update_session(
    document: str,
    session_id: str,
    data: SessionUpdate,
    current_user: UserOut = Depends(require_roles("medico", "admin", "super_admin")),
):
    db = get_db()
    if db is None:
        raise HTTPException(status_code=503, detail="Base de datos no disponible")

    existing = await db.sessions.find_one({"_id": ObjectId(session_id), "document_number": document})
    if not existing:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")

    update = {}
    if data.symptoms:
        update["symptoms"] = data.symptoms
    if data.diagnoses:
        update["diagnoses"] = data.diagnoses
    if data.treatment is not None:
        update["treatment"] = data.treatment
    if data.report_html:
        update["report_html"] = data.report_html
    if data.triage_level:
        update["triage_level"] = data.triage_level
    if data.triage_system:
        update["triage_system"] = data.triage_system
    if data.triage_discriminators:
        update["triage_discriminators"] = data.triage_discriminators
    if data.triage_score:
        update["triage_score"] = data.triage_score
    if data.labs is not None:
        update["labs"] = data.labs
    if data.doctor_review is not None:
        update["doctor_review"] = data.doctor_review

    if update:
        await db.sessions.update_one(
            {"_id": ObjectId(session_id)},
            {"$set": update},
        )
        # Also update clinical_histories timestamp
        await db.clinical_histories.update_one(
            {"document_number": document},
            {"$set": {"updated_at": datetime.utcnow()}},
        )

    updated = await db.sessions.find_one({"_id": ObjectId(session_id)})
    return session_to_out(updated)
