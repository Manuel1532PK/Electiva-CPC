"""Regenera el HTML/PDF de las historias clínicas ya persistidas.

Uso:
    backend/.venv/Scripts/python.exe backend/regenerate_reports.py
    backend/.venv/Scripts/python.exe backend/regenerate_reports.py --dry-run
    backend/.venv/Scripts/python.exe backend/regenerate_reports.py --document 1020304050

Solo escribe `report_html` en la colección `sessions`; no modifica datos
clínicos, diagnósticos, tratamientos ni marcas de demo.
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.database.mongodb import close_db, connect_db, get_db
from app.reports.history_document import build_report_model, render_report_html


def _time_label(value) -> str:
    if isinstance(value, datetime):
        return value.strftime("%I:%M %p").lstrip("0")
    return ""


def build_patient_info(history: dict, session: dict) -> dict:
    first = history.get("first_name", "")
    last = history.get("last_name", "")
    city = history.get("city", "")
    department = history.get("department", "")
    labs = session.get("labs") or {}

    return {
        "first_name": first,
        "last_name": last,
        "name": f"{first} {last}".strip(),
        "document_type": history.get("document_type", ""),
        "id_document": history.get("document_number", ""),
        "document_number": history.get("document_number", ""),
        "birth_date": history.get("birth_date", ""),
        "age": history.get("age", ""),
        "gender": history.get("gender", ""),
        "occupation": history.get("occupation", ""),
        "phone": history.get("phone", ""),
        "country": history.get("country", ""),
        "department": department,
        "city": city,
        "location": ", ".join(x for x in (city, department) if x),
        "consultation_reason": session.get("consultation_reason", ""),
        "symptom_evolution": session.get("symptom_evolution", ""),
        "tobacco": session.get("tobacco", ""),
        "alcohol": session.get("alcohol", ""),
        "substances": session.get("substances", ""),
        "physical_activity": session.get("physical_activity", ""),
        "pregnancy": session.get("pregnancy", ""),
        "medical_history": session.get("medical_history", ""),
        "surgical_history": session.get("surgical_history", ""),
        "pharmacological_history": session.get("pharmacological_history", ""),
        "allergies": session.get("allergies", ""),
        "blood_pressure": session.get("blood_pressure", ""),
        "heart_rate": session.get("heart_rate", ""),
        "respiratory_rate": session.get("respiratory_rate", ""),
        "temperature": session.get("temperature", ""),
        "oxygen_saturation": session.get("oxygen_saturation", ""),
        "weight": session.get("weight", ""),
        "height": session.get("height", ""),
        "triage_level": session.get("triage_level", 0),
        "triage_system": session.get("triage_system", ""),
        "triage_discriminators": session.get("triage_discriminators", ""),
        "triage_score": session.get("triage_score", ""),
        "lab_pao2": labs.get("pao2", ""),
        "lab_lactate": labs.get("lactate", ""),
        "lab_leukocytes": labs.get("leukocytes", ""),
        "lab_creatinine": labs.get("creatinine", ""),
        "lab_crp": labs.get("crp", ""),
    }


async def regenerate(*, dry_run: bool, document: str | None) -> int:
    if not await connect_db():
        print("[ERROR] No se pudo conectar a MongoDB en 127.0.0.1:27017.")
        return 1

    db = get_db()
    if db is None:
        print("[ERROR] Base de datos no disponible.")
        await close_db()
        return 1

    query: dict = {"report_html": {"$nin": ["", None]}}
    if document:
        query["document_number"] = document

    sessions = await db.sessions.find(query).sort("date", 1).to_list(length=1000)
    print(f"Sesiones con documento guardado: {len(sessions)}")

    histories = await db.clinical_histories.find({}).to_list(length=1000)
    by_document = {h.get("document_number"): h for h in histories}

    updated = 0
    skipped = 0
    for session in sessions:
        doc_number = session.get("document_number", "")
        history = by_document.get(doc_number)
        if not history:
            print(f"  [SKIP] {doc_number} sin historia clínica")
            skipped += 1
            continue

        encounter = {
            "date": session.get("date"),
            "start": _time_label(session.get("date")),
            "end": "",
            "doctor": session.get("doctor_name", ""),
            "hospital": session.get("hospital_name", ""),
        }
        model = build_report_model(
            patient_info=build_patient_info(history, session),
            symptoms=session.get("symptoms") or [],
            diagnoses=session.get("diagnoses") or [],
            treatment=session.get("treatment"),
            doctor_review=session.get("doctor_review") or {},
            encounter=encounter,
            generated_at=datetime.now(),
        )
        html = render_report_html(model)
        label = (
            f"{doc_number} · {session.get('date'):%Y-%m-%d}"
            if isinstance(session.get("date"), datetime)
            else f"{doc_number} · sin fecha"
        )

        if dry_run:
            print(f"  [DRY] {label} -> {len(html)} chars")
        else:
            await db.sessions.update_one({"_id": session["_id"]}, {"$set": {"report_html": html}})
            action = "UPDATED"
            print(f"  [{action}] {label} -> {len(html)} chars")
        updated += 1

    print(f"\nDocumentos regenerados: {updated} · omitidos: {skipped} · dry-run: {dry_run}")
    await close_db()
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Regenera las historias clínicas guardadas con el diseño actual.")
    parser.add_argument("--dry-run", action="store_true", help="Muestra el resultado sin escribir en MongoDB.")
    parser.add_argument("--document", default=None, help="Limita la migración a un número de documento.")
    args = parser.parse_args()
    return asyncio.run(regenerate(dry_run=args.dry_run, document=args.document))


if __name__ == "__main__":
    raise SystemExit(main())
