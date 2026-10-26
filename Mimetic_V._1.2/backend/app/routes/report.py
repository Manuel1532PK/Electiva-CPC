from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from bson import ObjectId
from app.expert_system.engine import diagnose, get_treatment, recommend_treatment
from app.database.mongodb import get_db
from app.auth.permissions import require_roles
from app.reports.history_document import build_report_model, render_report_html
from datetime import datetime

router = APIRouter()


class ReportRequest(BaseModel):
    patient_info: dict
    symptoms: list[str]
    selected_diagnosis: str | None = None
    doctor_review: dict | None = None
    session_id: Optional[str] = None
    document_number: Optional[str] = None


class ReportResponse(BaseModel):
    report: str
    html_report: str
    has_treatment: bool = False
    treatment: dict | None = None


# Helper: raw value without HTML escaping (for plain-text output)
def raw_val(pi, key, default=""):
    v = pi.get(key, "")
    return v if v else default


@router.post("/report", response_model=ReportResponse)
async def generate_report(
    request: ReportRequest,
    current_user=Depends(require_roles("medico", "admin", "super_admin")),
):
    pi = request.patient_info
    dr = request.doctor_review or {}
    doctor_notes = dr.get("doctorNotes", "")
    now = datetime.now()

    db = get_db()
    session_doc = None
    if request.session_id and db is not None:
        try:
            session_doc = await db.sessions.find_one({"_id": ObjectId(request.session_id)})
        except Exception:
            session_doc = None

    session_date = session_doc.get("date") if session_doc else None
    if isinstance(session_date, datetime):
        report_date = session_date
        date_str = session_date.strftime("%d / %m / %Y")
        session_time = session_date.strftime("%I:%M %p").lstrip("0")
    else:
        report_date = now
        date_str = now.strftime("%d / %m / %Y")
        session_time = now.strftime("%I:%M %p").lstrip("0")

    time_str = now.strftime("%I:%M %p").lstrip("0")
    hour_start_raw = pi.get("consultation_start") or session_time
    hour_end = time_str
    gender_map = {"m": "Masculino", "f": "Femenino", "otro": "Otro"}

    results = await diagnose(request.symptoms, patient_info=request.patient_info) if request.symptoms else []
    tx = None
    if request.selected_diagnosis:
        tx = await recommend_treatment(request.selected_diagnosis, request.patient_info)
        if not tx or not tx.get("available"):
            tx = await get_treatment(request.selected_diagnosis)

    has_tx = tx is not None

    encounter = {
        "date": report_date,
        "start": hour_start_raw,
        "end": time_str,
        "doctor": (session_doc or {}).get("doctor_name") or getattr(current_user, "name", ""),
        "hospital": (session_doc or {}).get("hospital_name", ""),
    }

    model = build_report_model(
        patient_info=pi,
        symptoms=request.symptoms,
        diagnoses=results,
        treatment=tx,
        doctor_review=dr,
        encounter=encounter,
        generated_at=now,
    )
    html_report = render_report_html(model)

    # Plain text (uses raw, unescaped values)
    text_doc_type = raw_val(pi, "document_type", "CC")
    text_doc_num = raw_val(pi, "id_document")
    text_doc_full = f"{text_doc_type} N° {text_doc_num}" if text_doc_num else ""
    text_gender = raw_val(pi, "gender")
    text_gender_display = gender_map.get(text_gender.lower(), text_gender) if text_gender else ""

    text = f"""=== HISTORIA CLÍNICA ===
MIMETIC - Sistema de Apoyo al Diagnóstico Médico
Fecha: {date_str} - {time_str}

--- 1. Información General ---
Fecha: {date_str} | Inicio: {hour_start_raw} | Cierre: {hour_end}

--- 2. Identificación del Paciente ---
Nombre: {raw_val(pi, "name")}
Documento: {text_doc_full}
Edad: {raw_val(pi, "age")} | Género: {text_gender_display}
Ocupación: {raw_val(pi, "occupation")} | Teléfono: {raw_val(pi, "phone")}
Ciudad: {raw_val(pi, "location")}

--- 3. Anamnesis ---
Motivo: {raw_val(pi, "consultation_reason")}
Evolución: {raw_val(pi, "symptom_evolution")}
Síntomas: {', '.join(request.symptoms) if request.symptoms else 'No reportados'}

--- 4. Antecedentes ---
Tabaco: {raw_val(pi, "tobacco")} | Alcohol: {raw_val(pi, "alcohol")}
Sustancias: {raw_val(pi, "substances")} | Actividad: {raw_val(pi, "physical_activity")}
Médicos: {raw_val(pi, "medical_history")}
Quirúrgicos: {raw_val(pi, "surgical_history")}
Farmacológicos: {raw_val(pi, "pharmacological_history")}
Alergias: {raw_val(pi, "allergies")}

--- 5. Signos Vitales ---
PA: {raw_val(pi, "blood_pressure")} | FC: {raw_val(pi, "heart_rate")} | FR: {raw_val(pi, "respiratory_rate")}
Temp: {raw_val(pi, "temperature")} | Peso: {raw_val(pi, "weight")} | Estatura: {raw_val(pi, "height")}

--- 6. Diagnósticos ---
"""

    if results:
        for d in results:
            text += f"- {d['disease_name']} ({d['confidence']:.0%}) - {d.get('severity', '')}\n"

    if tx:
        text += f"\n--- 7. Receta Médica ---\nDiagnóstico: {tx.get('disease_name', '')}\n"
        meds_list = tx.get("available", tx.get("medicines", []))
        for m in meds_list:
            text += f"{m['name']} - {m.get('dosage', '')} - {m.get('frequency', '')} - {m.get('duration', '')}\n"
        alt_list = tx.get("alternatives", tx.get("alternative_medicines", []))
        if alt_list:
            text += "\nAlternativos:\n"
            for m in alt_list:
                text += f"{m['name']} - {m.get('dosage', '')} - {m.get('frequency', '')} - {m.get('duration', '')}\n"
        if tx.get("general_recommendations"):
            text += f"\n--- 8. Recomendaciones ---\n{tx['general_recommendations']}\n"

    if doctor_notes:
        text += f"\n--- 9. Observaciones del Médico ---\n{doctor_notes}\n"

    text += "\n=== Fin del Reporte ==="

    # Persist session data if session_id and document_number provided
    if request.session_id and request.document_number:
        db = get_db()
        if db is not None:
            update = {"symptoms": request.symptoms}
            if dr:
                update["doctor_review"] = dr
            if results:
                update["diagnoses"] = results
            if tx:
                update["treatment"] = tx
            if html_report:
                update["report_html"] = html_report

            try:
                await db.sessions.update_one(
                    {"_id": ObjectId(request.session_id), "document_number": request.document_number},
                    {"$set": update},
                )
                await db.clinical_histories.update_one(
                    {"document_number": request.document_number},
                    {"$set": {"updated_at": datetime.utcnow()}},
                )
            except Exception:
                pass  # Non-critical: report still returns

    return ReportResponse(
        report=text,
        html_report=html_report,
        has_treatment=has_tx,
        treatment=tx,
    )
