from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
from bson import ObjectId
from app.database.mongodb import get_db
from app.auth.permissions import require_roles
from app.models.user import UserOut
from app.models.clinical_history import (
    ClinicalHistoryOut,
    SessionOut,
    PatientSessionSummary,
    PatientTreatmentSummary,
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
        weight=s.get("weight", ""),
        height=s.get("height", ""),
        symptoms=s.get("symptoms", []),
        diagnoses=s.get("diagnoses", []),
        treatment=s.get("treatment"),
        report_html=s.get("report_html", ""),
    )


@router.get("/patient/clinical-history")
async def get_my_clinical_history(
    current_user: UserOut = Depends(require_roles("paciente")),
):
    db = get_db()
    if db is None:
        raise HTTPException(status_code=503, detail="Base de datos no disponible")

    doc_number = current_user.document_number
    if not doc_number:
        raise HTTPException(status_code=400, detail="No tiene número de documento registrado")

    hist = await db.clinical_histories.find_one({"document_number": doc_number})
    if not hist:
        return None

    return history_to_out(hist)


@router.get("/patient/sessions")
async def get_my_sessions(
    current_user: UserOut = Depends(require_roles("paciente")),
):
    db = get_db()
    if db is None:
        raise HTTPException(status_code=503, detail="Base de datos no disponible")

    doc_number = current_user.document_number
    if not doc_number:
        return []

    cursor = db.sessions.find({"document_number": doc_number}).sort("date", -1)
    sessions = await cursor.to_list(length=100)
    return [session_to_out(s) for s in sessions]


@router.get("/patient/sessions/{session_id}")
async def get_my_session_detail(
    session_id: str,
    current_user: UserOut = Depends(require_roles("paciente")),
):
    db = get_db()
    if db is None:
        raise HTTPException(status_code=503, detail="Base de datos no disponible")

    doc_number = current_user.document_number
    if not doc_number:
        raise HTTPException(status_code=400, detail="No tiene número de documento registrado")

    session = await db.sessions.find_one({"_id": ObjectId(session_id), "document_number": doc_number})
    if not session:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")

    return session_to_out(session)


@router.get("/patient/treatments")
async def get_my_treatments(
    current_user: UserOut = Depends(require_roles("paciente")),
):
    db = get_db()
    if db is None:
        raise HTTPException(status_code=503, detail="Base de datos no disponible")

    doc_number = current_user.document_number
    if not doc_number:
        return []

    cursor = db.sessions.find(
        {"document_number": doc_number, "treatment": {"$ne": None}},
        {"treatment": 1, "date": 1, "hospital_name": 1, "diagnoses": 1}
    ).sort("date", -1)
    sessions = await cursor.to_list(length=100)

    treatments = []
    for s in sessions:
        tx = s.get("treatment", {})
        if not tx:
            continue

        disease_name = tx.get("disease_name", "")
        if tx.get("available"):
            medicines = tx["available"]
        elif tx.get("medicines"):
            medicines = tx["medicines"]
        else:
            medicines = []

        treatments.append(PatientTreatmentSummary(
            disease_name=disease_name,
            medicines=medicines,
            general_recommendations=tx.get("general_recommendations", ""),
            session_date=s.get("date", datetime.utcnow()),
            hospital_name=s.get("hospital_name", ""),
        ))

    return treatments


@router.get("/patient/summary")
async def get_my_summary(
    current_user: UserOut = Depends(require_roles("paciente")),
):
    db = get_db()
    if db is None:
        raise HTTPException(status_code=503, detail="Base de datos no disponible")

    doc_number = current_user.document_number
    if not doc_number:
        return {
            "total_sessions": 0,
            "total_diagnoses": 0,
            "hospitals_visited": [],
            "last_session_date": None,
            "last_diagnosis": None,
            "recent_sessions": [],
        }

    cursor = db.sessions.find({"document_number": doc_number}).sort("date", -1)
    sessions = await cursor.to_list(length=100)

    total_sessions = len(sessions)
    all_diagnoses = []
    hospitals_visited = set()
    last_session_date = None
    last_diagnosis = None

    for s in sessions:
        if not last_session_date:
            last_session_date = s.get("date")

        hn = s.get("hospital_name", "")
        if hn:
            hospitals_visited.add(hn)

        diags = s.get("diagnoses", [])
        for d in diags:
            d_name = d.get("disease_name", "")
            if d_name:
                all_diagnoses.append(d_name)
                if not last_diagnosis:
                    last_diagnosis = d_name

    recent_sessions = []
    for s in sessions[:5]:
        diags = s.get("diagnoses", [])
        recent_sessions.append(PatientSessionSummary(
            id=str(s["_id"]),
            date=s.get("date", datetime.utcnow()),
            hospital_name=s.get("hospital_name", ""),
            doctor_name=s.get("doctor_name", ""),
            consultation_reason=s.get("consultation_reason", ""),
            diagnoses=diags,
            has_treatment=s.get("treatment") is not None,
            symptoms=s.get("symptoms", []),
        ))

    return {
        "total_sessions": total_sessions,
        "total_diagnoses": len(set(all_diagnoses)),
        "hospitals_visited": list(hospitals_visited),
        "last_session_date": last_session_date,
        "last_diagnosis": last_diagnosis,
        "recent_sessions": recent_sessions,
    }
