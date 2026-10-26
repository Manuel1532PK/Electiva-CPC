"""Plantilla print-first de la historia clínica MIMETIC.

El HTML resultante se usa tanto en la vista previa como en el diálogo de
impresión del navegador («Guardar como PDF»). No depende de JavaScript ni de
recursos externos: tipografías del sistema, CSS embebido y tamaños Letter.
"""

from __future__ import annotations

import html
import re
from datetime import datetime
from typing import Any

MONTHS_ES = (
    "ene", "feb", "mar", "abr", "may", "jun",
    "jul", "ago", "sep", "oct", "nov", "dic",
)

TRIAGE_LEVELS = {
    1: "Nivel 1 · Rojo · Atención inmediata",
    2: "Nivel 2 · Naranja · Emergencia",
    3: "Nivel 3 · Amarillo · Urgente",
    4: "Nivel 4 · Verde · Estándar",
    5: "Nivel 5 · Azul · No urgente",
}

GENDER_MAP = {"m": "Masculino", "f": "Femenino", "otro": "Otro"}


# ── Helpers ───────────────────────────────────────────────────────

def _e(value: Any) -> str:
    if value is None:
        return ""
    return html.escape(str(value), quote=True)


def _text(value: Any) -> str:
    """Escapa y conserva saltos de línea en narrativas."""
    return _e(value).replace("\r\n", "\n").replace("\n", "<br>")


def _s(value: Any) -> str:
    return "" if value is None else str(value).strip()


def _fmt_date(value: Any) -> str:
    dt: datetime | None = None
    if isinstance(value, datetime):
        dt = value
    elif isinstance(value, str) and value.strip():
        raw = value.strip().replace("Z", "+00:00")
        try:
            dt = datetime.fromisoformat(raw)
        except ValueError:
            return value.strip()
    if not dt:
        return ""
    return f"{dt.day:02d} {MONTHS_ES[dt.month - 1]} {dt.year}"


def _fmt_time(value: Any) -> str:
    if isinstance(value, datetime):
        return value.strftime("%I:%M %p").lstrip("0")
    return _s(value)


def _initials(name: str) -> str:
    words = [w for w in re.split(r"\s+", name.strip()) if w]
    if not words:
        return "MI"
    if len(words) == 1:
        return words[0][:2].upper()
    return (words[0][0] + words[-1][0]).upper()


def _pct(value: Any) -> int:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return 0
    if number <= 1:
        number *= 100
    return max(0, min(100, round(number)))


def _gender(value: Any) -> str:
    raw = _s(value)
    if not raw:
        return ""
    return GENDER_MAP.get(raw.lower(), raw)


def _split_sentences(value: Any) -> list[str]:
    text = _s(value)
    if not text:
        return []
    parts = re.split(r"(?<=[.!?])\s+|\n+", text)
    return [p.strip(" -•\t") for p in parts if p.strip(" -•\t")]


def _trim(value: Any, limit: int = 170) -> str:
    text = _s(value)
    if len(text) <= limit:
        return text
    cut = text[:limit].rsplit(" ", 1)[0]
    return f"{cut}…"


# ── Modelo de datos ───────────────────────────────────────────────

def build_report_model(
    patient_info: dict | None,
    symptoms: list[str] | None,
    diagnoses: list[dict] | None,
    treatment: dict | None,
    doctor_review: dict | None,
    encounter: dict | None = None,
    generated_at: datetime | None = None,
) -> dict:
    """Normaliza los datos clínicos que consume la plantilla."""
    pi = patient_info or {}
    dr = doctor_review or {}
    enc = encounter or {}
    now = generated_at or datetime.now()

    first = _s(pi.get("first_name"))
    last = _s(pi.get("last_name"))
    name = _s(pi.get("name")) or " ".join(x for x in (first, last) if x).strip() or "Paciente sin identificar"

    location = _s(pi.get("location"))
    if not location:
        city = _s(pi.get("city"))
        department = _s(pi.get("department"))
        location = ", ".join(x for x in (city, department) if x)

    patient = {
        "name": name,
        "initials": _initials(name),
        "doc_type": _s(pi.get("document_type")) or "CC",
        "doc_number": _s(pi.get("id_document")) or _s(pi.get("document_number")) or "Sin documento",
        "birth_date": _s(pi.get("birth_date")),
        "age": _s(pi.get("age")),
        "gender": _gender(pi.get("gender")),
        "occupation": _s(pi.get("occupation")),
        "phone": _s(pi.get("phone")),
        "location": location,
    }

    declared_date = enc.get("date")
    if declared_date:
        date_label = _fmt_date(declared_date)
        start_default = _fmt_time(declared_date)
    else:
        date_label = _fmt_date(now)
        start_default = _fmt_time(now)

    start = _s(enc.get("start")) or _s(pi.get("consultation_start")) or start_default
    end = _s(enc.get("end"))
    if not end and not enc.get("date"):
        end = _fmt_time(now)

    encounter_model = {
        "date": date_label,
        "start": start,
        "end": end,
        "doctor": _s(enc.get("doctor")),
        "hospital": _s(enc.get("hospital")),
        "reason": _s(pi.get("consultation_reason")),
        "generated_date": _fmt_date(now),
        "generated_time": _fmt_time(now),
    }

    vitals_spec = (
        ("Presión arterial", "blood_pressure", "mmHg", "01"),
        ("Frecuencia cardíaca", "heart_rate", "lpm", "02"),
        ("Frecuencia respiratoria", "respiratory_rate", "rpm", "03"),
        ("Temperatura", "temperature", "°C", "04"),
        ("Saturación O₂", "oxygen_saturation", "%", "05"),
        ("Peso / talla", "weight", "kg / cm", "06"),
    )
    vitals: list[dict] = []
    for label, key, unit, index in vitals_spec:
        if key == "weight":
            weight = _s(pi.get("weight"))
            height = _s(pi.get("height"))
            if not weight and not height:
                continue
            if weight and height:
                value = f"{weight} / {height}"
            elif weight:
                value = weight
                unit = "kg"
            else:
                value = height
                unit = "cm"
            vitals.append({"label": label, "value": value, "unit": unit, "index": index})
        else:
            value = _s(pi.get(key))
            if value:
                vitals.append({"label": label, "value": value, "unit": unit, "index": index})

    try:
        triage_number = int(pi.get("triage_level") or 0)
    except (TypeError, ValueError):
        triage_number = 0
    triage_score = _s(pi.get("triage_score"))
    triage_discriminators = _s(pi.get("triage_discriminators"))
    triage_system = _s(pi.get("triage_system"))
    triage = None
    if triage_number or triage_score or triage_discriminators:
        triage = {
            "number": triage_number,
            "label": TRIAGE_LEVELS.get(triage_number, "Sin clasificar"),
            "system": triage_system,
            "score": triage_score,
            "discriminators": triage_discriminators,
        }

    labs_spec = (
        ("pO₂ arterial", "lab_pao2", "mmHg"),
        ("Lactato", "lab_lactate", "mmol/L"),
        ("Leucocitos", "lab_leukocytes", "10³/µL"),
        ("Creatinina", "lab_creatinine", "mg/dL"),
        ("Proteína C reactiva", "lab_crp", "mg/L"),
    )
    labs = [
        {"label": label, "value": _s(pi.get(key)), "unit": unit}
        for label, key, unit in labs_spec
        if _s(pi.get(key))
    ]

    confirmed_names = [_s(x) for x in (dr.get("confirmedDiagnoses") or []) if _s(x)]
    confirmed: list[dict] = [
        {"name": label, "origin": "Confirmado por el médico", "notes": ""}
        for label in confirmed_names
    ]
    for item in dr.get("manualDiagnoses") or []:
        if not isinstance(item, dict):
            continue
        label = _s(item.get("disease_name"))
        if not label:
            continue
        confirmed.append(
            {
                "name": label,
                "origin": "Diagnóstico manual",
                "notes": _s(item.get("notes")),
            }
        )

    differential: list[dict] = []
    for item in diagnoses or []:
        if not isinstance(item, dict):
            continue
        label = _s(item.get("disease_name"))
        if not label or label in confirmed_names:
            continue
        differential.append(
            {
                "name": label,
                "severity": _s(item.get("severity")),
                "confidence": _pct(item.get("confidence")),
                "description": _trim(item.get("description")),
            }
        )

    prescription = None
    if treatment:
        is_new = "available" in treatment
        meds = treatment.get("available", []) if is_new else treatment.get("medicines", [])
        not_recommended = treatment.get("not_recommended", []) if is_new else []
        alternatives = (
            treatment.get("alternatives", [])
            if is_new
            else treatment.get("alternative_medicines", [])
        )
        non_pharm = (
            treatment.get("non_pharmacological", [])
            if is_new
            else treatment.get("non_pharmacological_treatments", [])
        )

        selected = [_s(x) for x in (dr.get("selectedMedicines") or []) if _s(x)]
        if selected:
            meds = [m for m in meds if isinstance(m, dict) and _s(m.get("name")) in selected]
            alternatives = [
                m for m in alternatives if isinstance(m, dict) and _s(m.get("name")) in selected
            ]

        modified = dr.get("modifiedDoses") or {}

        def med_model(med: dict, flagged: bool = False) -> dict:
            name_med = _s(med.get("name"))
            alerts: list[dict] = []
            if flagged:
                alerts.append({"tone": "danger", "text": "No recomendado para este paciente."})

            contra = med.get("contraindications") or {}
            if isinstance(contra, dict):
                if contra.get("allergies"):
                    alerts.append(
                        {
                            "tone": "warn",
                            "text": "Alergias: " + ", ".join(_s(a) for a in contra["allergies"] if _s(a)),
                        }
                    )
                if contra.get("conditions"):
                    alerts.append(
                        {
                            "tone": "warn",
                            "text": "Contraindicado en: "
                            + ", ".join(_s(c) for c in contra["conditions"] if _s(c)),
                        }
                    )

            adjustments = med.get("adjustments") or {}
            if isinstance(adjustments, dict):
                labels = {
                    "renal": "Renal",
                    "hepatic": "Hepático",
                    "pediatric": "Pediátrico",
                    "geriatric": "Geriátrico",
                    "pregnancy": "Embarazo",
                }
                for key, label in labels.items():
                    if _s(adjustments.get(key)):
                        alerts.append(
                            {"tone": "warn", "text": f"{label}: {_s(adjustments.get(key))}"}
                        )

            if _s(med.get("interactions_warning")):
                alerts.append({"tone": "danger", "text": _s(med.get("interactions_warning"))})

            dosage = _s(modified.get(name_med)) or _s(med.get("dosage"))
            return {
                "name": name_med,
                "dosage": dosage,
                "adjusted": bool(_s(modified.get(name_med))),
                "route": _s(med.get("route")) or "Oral",
                "frequency": _s(med.get("frequency")),
                "duration": _s(med.get("duration")),
                "monitoring": _s(med.get("monitoring")),
                "summary": _s(med.get("patient_summary")),
                "alerts": alerts,
            }

        prescription = {
            "diagnosis": _s(treatment.get("disease_name")),
            "medicines": [med_model(m) for m in meds if isinstance(m, dict)],
            "not_recommended": [med_model(m, True) for m in not_recommended if isinstance(m, dict)],
            "alternatives": [med_model(m) for m in alternatives if isinstance(m, dict)],
            "non_pharm": [x for x in non_pharm if isinstance(x, str) and x.strip()],
            "recommendations": _split_sentences(treatment.get("general_recommendations")),
        }

    return {
        "patient": patient,
        "encounter": encounter_model,
        "anamnesis": {
            "reason": _s(pi.get("consultation_reason")),
            "evolution": _s(pi.get("symptom_evolution")),
        },
        "symptoms": [x for x in (symptoms or []) if _s(x)],
        "background": {
            "tobacco": _s(pi.get("tobacco")),
            "alcohol": _s(pi.get("alcohol")),
            "substances": _s(pi.get("substances")),
            "physical_activity": _s(pi.get("physical_activity")),
            "pregnancy": _s(pi.get("pregnancy")),
            "medical": _s(pi.get("medical_history")),
            "surgical": _s(pi.get("surgical_history")),
            "pharmacological": _s(pi.get("pharmacological_history")),
            "allergies": _s(pi.get("allergies")),
        },
        "vitals": vitals,
        "triage": triage,
        "labs": labs,
        "diagnoses": {
            "confirmed": confirmed,
            "differential": differential,
        },
        "prescription": prescription,
        "recommendations": (prescription or {}).get("recommendations", []),
        "notes": _s(dr.get("doctorNotes")),
    }


# ── Render ────────────────────────────────────────────────────────

_CSS = """
@page { size: Letter; margin: 12mm 11mm; }
* { box-sizing: border-box; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body {
  margin: 0;
  background: #e9eef5;
  color: #0f172a;
  font-family: 'Inter', 'Segoe UI', -apple-system, BlinkMacSystemFont, Arial, sans-serif;
  font-size: 9.4pt;
  line-height: 1.5;
  -webkit-font-smoothing: antialiased;
}
.doc {
  width: 8.5in;
  max-width: calc(100% - 8px);
  margin: 18px auto;
  padding: 9mm 10mm 8mm;
  background: #ffffff;
  border-radius: 2px;
  box-shadow: 0 28px 60px -34px rgba(11, 53, 88, .55);
}
p { margin: 0; }
h1, h2, h3 { margin: 0; }
.mono { font-family: 'JetBrains Mono', 'Consolas', 'SFMono-Regular', monospace; }
.eyebrow {
  display: block;
  font-size: 6.5pt;
  font-weight: 800;
  letter-spacing: .16em;
  text-transform: uppercase;
  color: #0284c7;
}
.eyebrow.light { color: #7dd3fc; }

/* Masthead */
.masthead {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 18px;
  padding: 14px 18px;
  border-radius: 14px;
  border-bottom: 3px solid #38bdf8;
  background:
    radial-gradient(circle at 82% 0%, rgba(56, 189, 248, .18), transparent 48%),
    linear-gradient(135deg, #0b3558 0%, #062642 100%);
  color: #ffffff;
}
.brand { display: flex; align-items: center; gap: 10px; }
.brand-mark {
  width: 36px; height: 36px;
  display: flex; align-items: center; justify-content: center;
  border-radius: 10px;
  background: linear-gradient(135deg, #0ea5e9, #0284c7);
  border: 1px solid rgba(255, 255, 255, .28);
  color: #ffffff;
  font-size: 15pt;
  font-weight: 800;
  letter-spacing: -.03em;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, .3);
}
.brand-name {
  font-family: 'Plus Jakarta Sans', 'Segoe UI', Arial, sans-serif;
  font-size: 11.5pt;
  font-weight: 800;
  letter-spacing: .24em;
  line-height: 1.1;
}
.brand-tag {
  margin-top: 3px;
  font-size: 6.4pt;
  font-weight: 700;
  letter-spacing: .18em;
  text-transform: uppercase;
  color: #7dd3fc;
}
.masthead-meta { text-align: right; }
.masthead-title {
  font-family: 'Plus Jakarta Sans', 'Segoe UI', Arial, sans-serif;
  margin-top: 2px;
  font-size: 12.5pt;
  font-weight: 700;
  letter-spacing: -.01em;
}
.masthead-line {
  margin-top: 2px;
  font-size: 7.3pt;
  color: #cbd5e1;
  letter-spacing: .02em;
}
.masthead-line strong { color: #ffffff; font-weight: 700; }

.syncbar {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 4px 0;
  font-size: 6.7pt;
  font-weight: 700;
  letter-spacing: .12em;
  text-transform: uppercase;
  color: #64748b;
}
.sync-dot {
  width: 5px; height: 5px;
  border-radius: 50%;
  background: #10b981;
  box-shadow: 0 0 0 3px rgba(16, 185, 129, .15);
}
.syncbar .spacer { flex: 1; }
.sync-chip {
  padding: 2px 6px;
  border-radius: 999px;
  border: 1px solid #e2e8f0;
  background: #f8fafc;
  color: #475569;
  font-size: 6.2pt;
  letter-spacing: .08em;
}
.sync-chip.demo { border-color: #fde68a; background: #fffbeb; color: #92400e; }

/* Patient */
.patient-card {
  display: grid;
  grid-template-columns: 1fr 2.35in;
  gap: 16px;
  margin-top: 12px;
  padding: 14px 16px;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
}
.patient-card > * { min-width: 0; }
.patient-main { display: flex; gap: 12px; align-items: center; }
.avatar {
  width: 46px; height: 46px;
  flex: 0 0 46px;
  display: flex; align-items: center; justify-content: center;
  border-radius: 12px;
  border: 1px solid #bae6fd;
  background: linear-gradient(135deg, #e0f2fe, #bae6fd);
  color: #0b3558;
  font-family: 'Plus Jakarta Sans', 'Segoe UI', Arial, sans-serif;
  font-size: 14pt;
  font-weight: 800;
}
.patient-name {
  font-family: 'Plus Jakarta Sans', 'Segoe UI', Arial, sans-serif;
  margin-top: 1px;
  font-size: 15pt;
  font-weight: 800;
  letter-spacing: -.02em;
  color: #0b3558;
}
.chips { display: flex; flex-wrap: wrap; gap: 4px; margin-top: 4px; }
.chip {
  display: inline-flex; align-items: center; gap: 3px;
  padding: 1.5px 7px;
  border: 1px solid #e2e8f0;
  border-radius: 999px;
  background: #ffffff;
  color: #475569;
  font-size: 6.6pt;
  font-weight: 700;
  letter-spacing: .05em;
  text-transform: uppercase;
}
.chip.chip-id { border-color: #bae6fd; background: #f0f9ff; color: #075985; letter-spacing: .02em; }
.patient-meta { display: flex; flex-wrap: wrap; gap: 3px 12px; margin-top: 5px; font-size: 7.3pt; color: #64748b; }
.patient-meta strong { color: #334155; font-weight: 600; }
.patient-side {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 5px 12px;
  align-content: center;
  padding-left: 14px;
  border-left: 1px dashed #cbd5e1;
}
.meta-item .meta-label {
  display: block;
  font-size: 6pt;
  font-weight: 800;
  letter-spacing: .13em;
  text-transform: uppercase;
  color: #94a3b8;
}
.meta-item .meta-value {
  display: block;
  margin-top: 1px;
  font-size: 8pt;
  font-weight: 600;
  color: #0b3558;
}

/* Sections */
.section { margin-top: 15px; }
.section-head {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  padding-bottom: 5px;
  border-bottom: 1px solid #e2e8f0;
  break-after: avoid;
}
.section-num {
  width: 21px; height: 21px;
  flex: 0 0 21px;
  display: flex; align-items: center; justify-content: center;
  border-radius: 6px;
  background: #e0f2fe;
  color: #0369a1;
  font-family: 'JetBrains Mono', Consolas, monospace;
  font-size: 7.3pt;
  font-weight: 700;
}
.section-title h2 {
  margin-top: 1px;
  font-family: 'Plus Jakarta Sans', 'Segoe UI', Arial, sans-serif;
  font-size: 10.4pt;
  font-weight: 700;
  letter-spacing: -.01em;
  color: #0b3558;
}
.section-head .head-aside { margin-left: auto; }

.panel {
  padding: 10px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  background: #ffffff;
}
.panel.soft { background: #f8fafc; }
.panel + .panel, .panel + .table, .table + .panel, .vitals + .panel { margin-top: 8px; }
.panel-title {
  display: block;
  margin-bottom: 4px;
  font-size: 6.3pt;
  font-weight: 800;
  letter-spacing: .14em;
  text-transform: uppercase;
  color: #94a3b8;
}
.reason { font-size: 10.6pt; font-weight: 700; color: #0b3558; line-height: 1.35; }
.narrative { margin-top: 4px; font-size: 8.5pt; color: #334155; line-height: 1.55; }
.narrative strong { color: #0b3558; }
.empty { font-size: 7.8pt; font-style: italic; color: #94a3b8; }
.empty-inline { font-size: 7.6pt; font-style: italic; color: #94a3b8; }

.chip-list { display: flex; flex-wrap: wrap; gap: 4px; margin-top: 6px; }
.symptom {
  padding: 2px 7px;
  border: 1px solid #bae6fd;
  border-radius: 999px;
  background: #f0f9ff;
  color: #075985;
  font-size: 7pt;
  font-weight: 600;
}

/* Background */
.split { display: grid; grid-template-columns: 1.05fr 1fr; gap: 8px; }
.risk-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 5px; }
.risk-item {
  padding: 6px 8px;
  border: 1px solid #eef2f7;
  border-radius: 8px;
  background: #f8fafc;
}
.risk-item span {
  display: block;
  font-size: 6pt;
  font-weight: 800;
  letter-spacing: .11em;
  text-transform: uppercase;
  color: #94a3b8;
}
.risk-item strong {
  display: block;
  margin-top: 2px;
  font-size: 7.8pt;
  font-weight: 600;
  color: #1e293b;
}
.flag { display: inline-flex; align-items: center; gap: 4px; font-size: 7.6pt; font-weight: 700; }
.flag::before { content: ''; width: 5px; height: 5px; border-radius: 50%; background: #94a3b8; }
.flag-yes { color: #047857; }
.flag-yes::before { background: #059669; box-shadow: 0 0 0 2px rgba(5, 150, 105, .14); }
.flag-no { color: #475569; }
.flag-no::before { background: #94a3b8; }
.flag-neutral { color: #92400e; }
.flag-neutral::before { background: #f59e0b; }

.kv { display: grid; gap: 5px; }
.kv-row {
  display: grid;
  grid-template-columns: 1.05in 1fr;
  gap: 8px;
  padding-bottom: 4px;
  border-bottom: 1px solid #f1f5f9;
}
.kv-row:last-child { border-bottom: 0; padding-bottom: 0; }
.kv-row dt { font-size: 6.6pt; font-weight: 700; letter-spacing: .06em; text-transform: uppercase; color: #64748b; }
.kv-row dd { margin: 0; font-size: 7.9pt; color: #1e293b; }
.allergy-line { margin-top: 7px; padding: 5px 8px; border-left: 3px solid #ef4444; background: #fef2f2; color: #991b1b; font-size: 7.6pt; border-radius: 0 6px 6px 0; }

/* Vitals */
.vitals { display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px; }
.vital {
  position: relative;
  padding: 8px 10px 9px;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  background: linear-gradient(180deg, #ffffff, #f8fafc);
  break-inside: avoid;
}
.vital .vital-label {
  display: block;
  padding-right: 18px;
  font-size: 6.2pt;
  font-weight: 800;
  letter-spacing: .11em;
  text-transform: uppercase;
  color: #64748b;
}
.vital .vital-value {
  display: flex;
  align-items: baseline;
  gap: 3px;
  margin-top: 2px;
}
.vital .vital-value b {
  font-family: 'JetBrains Mono', Consolas, monospace;
  font-size: 13pt;
  font-weight: 700;
  letter-spacing: -.02em;
  color: #0b3558;
}
.vital .vital-value span { font-size: 6.8pt; font-weight: 600; color: #94a3b8; }
.vital .vital-index {
  position: absolute;
  top: 7px; right: 9px;
  font-family: 'JetBrains Mono', Consolas, monospace;
  font-size: 6pt;
  color: #cbd5e1;
}

/* Triage */
.triage {
  margin-top: 8px;
  padding: 9px 11px;
  border: 1px solid #fcd34d;
  border-left: 4px solid #f59e0b;
  border-radius: 9px;
  background: linear-gradient(135deg, #fffbeb 0%, #ffffff 62%);
  break-inside: avoid;
}
.triage.level-1 { border-color: #fecaca; border-left-color: #dc2626; background: linear-gradient(135deg, #fef2f2, #ffffff 62%); }
.triage.level-2 { border-color: #fed7aa; border-left-color: #ea580c; background: linear-gradient(135deg, #fff7ed, #ffffff 62%); }
.triage.level-3 { border-color: #fde68a; border-left-color: #f59e0b; background: linear-gradient(135deg, #fffbeb, #ffffff 62%); }
.triage.level-4 { border-color: #a7f3d0; border-left-color: #059669; background: linear-gradient(135deg, #ecfdf5, #ffffff 62%); }
.triage.level-5 { border-color: #bae6fd; border-left-color: #0284c7; background: linear-gradient(135deg, #f0f9ff, #ffffff 62%); }
.triage-head { display: flex; align-items: center; gap: 8px; }
.triage-dot { width: 7px; height: 7px; border-radius: 50%; background: #f59e0b; box-shadow: 0 0 0 3px rgba(245, 158, 11, .18); }
.level-1 .triage-dot { background: #dc2626; box-shadow: 0 0 0 3px rgba(220, 38, 38, .16); }
.level-2 .triage-dot { background: #ea580c; box-shadow: 0 0 0 3px rgba(234, 88, 12, .16); }
.level-4 .triage-dot { background: #059669; box-shadow: 0 0 0 3px rgba(5, 150, 105, .16); }
.level-5 .triage-dot { background: #0284c7; box-shadow: 0 0 0 3px rgba(2, 132, 199, .16); }
.triage-title { margin-top: 1px; font-size: 9.6pt; font-weight: 800; color: #7c2d12; }
.level-1 .triage-title { color: #991b1b; }
.level-4 .triage-title { color: #065f46; }
.level-5 .triage-title { color: #075985; }
.triage-system {
  margin-left: auto;
  padding: 2px 7px;
  border: 1px solid rgba(120, 113, 108, .25);
  border-radius: 999px;
  background: rgba(255, 255, 255, .8);
  font-family: 'JetBrains Mono', Consolas, monospace;
  font-size: 6.4pt;
  font-weight: 700;
  color: #57534e;
}
.triage-grid { display: grid; grid-template-columns: 1.5fr 1fr; gap: 10px; margin-top: 7px; padding-top: 6px; border-top: 1px solid rgba(120, 113, 108, .18); }
.triage-grid .panel-title { margin-bottom: 2px; }
.triage-grid p { font-size: 7.5pt; color: #44403c; line-height: 1.45; }
.score-chips { display: flex; flex-wrap: wrap; gap: 4px; margin-top: 2px; }
.score-chip {
  padding: 2px 7px;
  border: 1px solid #bae6fd;
  border-radius: 5px;
  background: #f0f9ff;
  color: #075985;
  font-family: 'JetBrains Mono', Consolas, monospace;
  font-size: 7pt;
  font-weight: 700;
}

/* Tables */
.table { width: 100%; border-collapse: collapse; margin-top: 6px; }
.table th {
  padding: 4px 7px;
  border-bottom: 1px solid #cbd5e1;
  background: #f1f5f9;
  text-align: left;
  font-size: 6.2pt;
  font-weight: 800;
  letter-spacing: .1em;
  text-transform: uppercase;
  color: #475569;
}
.table td {
  padding: 5px 7px;
  border-bottom: 1px solid #f1f5f9;
  font-size: 7.9pt;
  color: #1e293b;
  vertical-align: top;
}
.table tr:last-child td { border-bottom: 0; }
.table .value { font-family: 'JetBrains Mono', Consolas, monospace; font-weight: 600; color: #0b3558; }
.table .unit { color: #94a3b8; font-size: 6.8pt; }
.table.compact td { padding: 3.5px 7px; }

/* Diagnoses */
.dx-list { display: grid; gap: 5px; }
.dx-card {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 10px;
  padding: 7px 10px;
  border: 1px solid #e2e8f0;
  border-left: 3px solid #0284c7;
  border-radius: 8px;
  background: #f8fafc;
  break-inside: avoid;
}
.dx-name { font-size: 9pt; font-weight: 700; color: #0b3558; }
.dx-note { margin-top: 2px; font-size: 7.4pt; color: #64748b; }
.dx-origin {
  flex: 0 0 auto;
  padding: 1.5px 7px;
  border: 1px solid #bae6fd;
  border-radius: 999px;
  background: #f0f9ff;
  color: #075985;
  font-size: 6.2pt;
  font-weight: 800;
  letter-spacing: .06em;
  text-transform: uppercase;
}
.subhead {
  margin: 10px 0 3px;
  font-size: 6.5pt;
  font-weight: 800;
  letter-spacing: .14em;
  text-transform: uppercase;
  color: #64748b;
}
.subhead:first-child { margin-top: 0; }
.conf { display: flex; align-items: center; gap: 6px; }
.bar { width: 52px; height: 4px; border-radius: 999px; background: #e2e8f0; overflow: hidden; }
.bar span { display: block; height: 100%; border-radius: 999px; background: linear-gradient(90deg, #38bdf8, #0284c7); }
.conf b { font-family: 'JetBrains Mono', Consolas, monospace; font-size: 7.2pt; color: #0b3558; }

/* Prescription */
.rx-diagnosis {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  margin-bottom: 2px;
  padding: 3px 9px;
  border: 1px solid #bae6fd;
  border-radius: 999px;
  background: #f0f9ff;
  color: #0b3558;
  font-size: 7.6pt;
  font-weight: 700;
}
.rx-diagnosis span { font-family: 'JetBrains Mono', Consolas, monospace; font-size: 6.1pt; font-weight: 800; letter-spacing: .1em; color: #0284c7; text-transform: uppercase; }
.med-table thead th { background: #0b3558; border-bottom: 0; color: #e2e8f0; }
.med-name { font-size: 8.2pt; font-weight: 700; color: #0b3558; }
.med-summary { margin-top: 2px; font-size: 6.8pt; color: #64748b; line-height: 1.4; }
.med-adjusted { margin-top: 2px; font-size: 6.6pt; font-weight: 700; color: #b45309; }
.route {
  display: inline-block;
  padding: 1px 5px;
  border: 1px solid #e2e8f0;
  border-radius: 4px;
  background: #f8fafc;
  font-family: 'JetBrains Mono', Consolas, monospace;
  font-size: 6.6pt;
  font-weight: 600;
  color: #475569;
  white-space: nowrap;
}
.alert { margin-top: 3px; padding: 2.5px 5px; border-radius: 4px; font-size: 6.5pt; line-height: 1.35; }
.alert-warn { border-left: 2px solid #f59e0b; background: #fffbeb; color: #92400e; }
.alert-danger { border-left: 2px solid #ef4444; background: #fef2f2; color: #991b1b; }
.nonpharm { display: flex; flex-wrap: wrap; gap: 4px; margin-top: 4px; }
.nonpharm span {
  padding: 2px 7px;
  border: 1px solid #a7f3d0;
  border-radius: 999px;
  background: #ecfdf5;
  color: #065f46;
  font-size: 6.9pt;
  font-weight: 600;
}

/* Recommendations & notes */
.rec-list { margin: 0; padding: 0; list-style: none; display: grid; gap: 5px; }
.rec-list li { position: relative; padding-left: 13px; font-size: 8.3pt; color: #334155; line-height: 1.5; }
.rec-list li::before {
  content: '';
  position: absolute;
  left: 1px; top: .52em;
  width: 5px; height: 5px;
  border-radius: 50%;
  background: #38bdf8;
  box-shadow: 0 0 0 2px #e0f2fe;
}
.note-card {
  padding: 9px 12px;
  border: 1px solid #e2e8f0;
  border-left: 3px solid #0284c7;
  border-radius: 0 9px 9px 0;
  background: #f8fafc;
  font-size: 8.4pt;
  color: #334155;
  line-height: 1.55;
}

/* Sign-off */
.signoff {
  display: grid;
  grid-template-columns: 1.35fr 1fr;
  gap: 14px;
  margin-top: 20px;
  padding-top: 12px;
  border-top: 1px solid #e2e8f0;
  break-inside: avoid;
}
.sig-line { height: 34px; border-bottom: 1px solid #94a3b8; }
.sig-name { margin-top: 5px; font-size: 8.5pt; font-weight: 700; color: #0b3558; }
.sig-role { font-size: 7pt; color: #64748b; }
.sig-license { margin-top: 2px; font-family: 'JetBrains Mono', Consolas, monospace; font-size: 6.4pt; color: #94a3b8; }
.stamp {
  padding: 8px 10px;
  border: 1px dashed #cbd5e1;
  border-radius: 9px;
  background: #f8fafc;
}
.stamp .panel-title { margin-bottom: 5px; }
.stamp-chips { display: flex; flex-wrap: wrap; gap: 4px; }
.stamp-chip {
  padding: 2px 6px;
  border: 1px solid #e2e8f0;
  border-radius: 4px;
  background: #ffffff;
  color: #64748b;
  font-family: 'JetBrains Mono', Consolas, monospace;
  font-size: 5.9pt;
  font-weight: 700;
  letter-spacing: .04em;
  text-transform: uppercase;
}
.stamp p { margin-top: 5px; font-size: 6.5pt; color: #94a3b8; line-height: 1.45; }

/* Footer */
.legal {
  margin-top: 14px;
  padding-top: 8px;
  border-top: 1px solid #e2e8f0;
  break-inside: avoid;
}
.legal-top { display: flex; align-items: center; justify-content: space-between; gap: 10px; }
.legal-brand {
  font-family: 'Plus Jakarta Sans', 'Segoe UI', Arial, sans-serif;
  font-size: 6.7pt;
  font-weight: 800;
  letter-spacing: .16em;
  text-transform: uppercase;
  color: #0b3558;
}
.legal-meta { font-family: 'JetBrains Mono', Consolas, monospace; font-size: 5.9pt; color: #94a3b8; }
.legal p { margin-top: 4px; font-size: 6.3pt; line-height: 1.5; color: #94a3b8; }

@media print {
  body { background: #ffffff; }
  .doc { width: auto; max-width: none; margin: 0; padding: 0; border-radius: 0; box-shadow: none; }
  .section { break-inside: auto; }
  .patient-card, .vitals, .triage, .dx-card, .note-card, .signoff, .legal { break-inside: avoid; }
  .masthead { border-radius: 10px; }
}
"""


def _empty(message: str = "Sin registro en esta atención.") -> str:
    return f'<p class="empty">{_e(message)}</p>'


def _section(number: str, eyebrow: str, title: str, body: str, aside: str = "") -> str:
    aside_html = f'<span class="head-aside">{aside}</span>' if aside else ""
    return f"""
    <section class="section">
      <div class="section-head">
        <span class="section-num">{_e(number)}</span>
        <div class="section-title">
          <span class="eyebrow">{_e(eyebrow)}</span>
          <h2>{_e(title)}</h2>
        </div>
        {aside_html}
      </div>
      {body}
    </section>"""


def _render_vitals(vitals: list[dict]) -> str:
    if not vitals:
        return _empty("No se registraron signos vitales.")
    tiles = "".join(
        f"""
        <div class="vital">
          <span class="vital-label">{_e(item['label'])}</span>
          <span class="vital-index">{_e(item['index'])}</span>
          <span class="vital-value"><b>{_e(item['value'])}</b><span>{_e(item['unit'])}</span></span>
        </div>"""
        for item in vitals
    )
    return f'<div class="vitals">{tiles}</div>'


def _render_triage(triage: dict | None) -> str:
    if not triage:
        return ""
    level = triage.get("number") or 0
    level_class = f" level-{level}" if level in (1, 2, 3, 4, 5) else ""
    system = f'<span class="triage-system">{_e(triage["system"])}</span>' if triage.get("system") else ""
    discriminators = triage.get("discriminators") or "Sin discriminadores registrados."
    scores = [s for s in re.split(r"\s*[·;|]\s*", _s(triage.get("score"))) if s]
    score_html = (
        "".join(f'<span class="score-chip">{_e(s)}</span>' for s in scores)
        if scores
        else '<span class="empty-inline">Sin puntuación</span>'
    )
    return f"""
    <div class="triage{level_class}">
      <div class="triage-head">
        <span class="triage-dot"></span>
        <div>
          <span class="panel-title">Clasificación de triaje</span>
          <div class="triage-title">{_e(triage['label'])}</div>
        </div>
        {system}
      </div>
      <div class="triage-grid">
        <div>
          <span class="panel-title">Discriminadores clínicos</span>
          <p>{_text(discriminators)}</p>
        </div>
        <div>
          <span class="panel-title">Puntuación de gravedad</span>
          <div class="score-chips">{score_html}</div>
        </div>
      </div>
    </div>"""


def _render_labs(labs: list[dict]) -> str:
    if not labs:
        return ""
    rows = "".join(
        f"""
        <tr>
          <td>{_e(item['label'])}</td>
          <td class="value">{_e(item['value'])} <span class="unit">{_e(item['unit'])}</span></td>
        </tr>"""
        for item in labs
    )
    return f"""
    <div class="panel">
      <span class="panel-title">Laboratorio urgente · valores de la sesión</span>
      <table class="table compact">
        <thead><tr><th>Determinación</th><th>Resultado</th></tr></thead>
        <tbody>{rows}</tbody>
      </table>
      <p class="empty" style="margin-top:5px;">La interpretación de estos valores corresponde al criterio médico.</p>
    </div>"""


def _render_background(bg: dict) -> str:
    habits = (
        ("Tabaco", bg.get("tobacco")),
        ("Alcohol", bg.get("alcohol")),
        ("Sustancias", bg.get("substances")),
        ("Actividad física", bg.get("physical_activity")),
        ("Embarazo", bg.get("pregnancy")),
    )

    def habit_value(value: str) -> str:
        if not value:
            return '<span class="empty-inline">Sin registro</span>'
        low = value.strip().lower()
        if low in ("si", "sí", "true", "activo"):
            return '<span class="flag flag-yes">Sí</span>'
        if low in ("no", "false", "ninguno", "ninguna", "n/a"):
            return '<span class="flag flag-no">No</span>'
        return f'<span class="flag flag-neutral">{_e(value)}</span>'

    habit_cards = "".join(
        f"""
        <div class="risk-item">
          <span>{_e(label)}</span>
          <strong>{habit_value(value)}</strong>
        </div>"""
        for label, value in habits
    )

    clinical = (
        ("Médicos / patológicos", bg.get("medical")),
        ("Quirúrgicos", bg.get("surgical")),
        ("Farmacológicos", bg.get("pharmacological")),
    )
    clinical_rows = "".join(
        f'<div class="kv-row"><dt>{_e(label)}</dt><dd>{_text(value) if value else "Sin registro"}</dd></div>'
        for label, value in clinical
    )
    allergies = (
        f'<div class="allergy-line"><strong>Alergias conocidas:</strong> {_text(bg.get("allergies"))}</div>'
        if bg.get("allergies")
        else ""
    )
    return f"""
    <div class="split">
      <div class="panel soft">
        <span class="panel-title">Hábitos y factores de riesgo</span>
        <div class="risk-grid">{habit_cards}</div>
        {allergies}
      </div>
      <div class="panel">
        <span class="panel-title">Antecedentes clínicos</span>
        <dl class="kv">{clinical_rows}</dl>
      </div>
    </div>"""


def _render_diagnoses(diag: dict) -> str:
    confirmed = diag.get("confirmed") or []
    differential = diag.get("differential") or []

    confirmed_html = ""
    if confirmed:
        cards = "".join(
            f"""
            <div class="dx-card">
              <div>
                <div class="dx-name">{_e(item['name'])}</div>
                {f'<div class="dx-note">{_text(item["notes"])}</div>' if item.get("notes") else ''}
              </div>
              <span class="dx-origin">{_e(item['origin'])}</span>
            </div>"""
            for item in confirmed
        )
        confirmed_html = f'<h3 class="subhead">Confirmados por el médico</h3><div class="dx-list">{cards}</div>'

    differential_html = ""
    if differential:
        rows = "".join(
            f"""
            <tr>
              <td><strong>{_e(item['name'])}</strong></td>
              <td>{_e(item['severity']) or '—'}</td>
              <td>
                <div class="conf">
                  <span class="bar"><span style="width:{item['confidence']}%"></span></span>
                  <b>{item['confidence']}%</b>
                </div>
              </td>
              <td>{_e(item['description']) or '—'}</td>
            </tr>"""
            for item in differential
        )
        differential_html = f"""
        <h3 class="subhead">Diferenciales sugeridos por la IA</h3>
        <table class="table compact">
          <thead><tr><th>Enfermedad</th><th>Severidad</th><th>Confianza</th><th>Descripción</th></tr></thead>
          <tbody>{rows}</tbody>
        </table>"""

    if not confirmed_html and not differential_html:
        return _empty("No se registraron diagnósticos en esta atención.")
    return confirmed_html + differential_html


def _render_med_table(medicines: list[dict]) -> str:
    if not medicines:
        return ""
    rows = ""
    for med in medicines:
        alerts = "".join(
            f'<div class="alert alert-{"danger" if alert.get("tone") == "danger" else "warn"}">{_text(alert.get("text"))}</div>'
            for alert in med.get("alerts") or []
        )
        summary = f'<div class="med-summary">{_text(med["summary"])}</div>' if med.get("summary") else ""
        adjusted = '<div class="med-adjusted">Dosis ajustada por el médico</div>' if med.get("adjusted") else ""
        rows += f"""
        <tr>
          <td>
            <div class="med-name">{_e(med['name'])}</div>
            {summary}{adjusted}{alerts}
          </td>
          <td class="value">{_e(med['dosage']) or '—'}</td>
          <td><span class="route">{_e(med['route']) or '—'}</span></td>
          <td>{_e(med['frequency']) or '—'}</td>
          <td>{_e(med['duration']) or '—'}</td>
          <td>{_e(med['monitoring']) or '—'}</td>
        </tr>"""
    return f"""
    <table class="table med-table">
      <thead>
        <tr><th>Medicamento</th><th>Dosis</th><th>Vía</th><th>Frecuencia</th><th>Duración</th><th>Monitoreo</th></tr>
      </thead>
      <tbody>{rows}</tbody>
    </table>"""


def _render_prescription(rx: dict | None) -> str:
    if not rx:
        return _empty("No se generó plan farmacológico para esta atención.")

    diagnosis = (
        f'<div class="rx-diagnosis"><span>Diagnóstico</span>{_e(rx["diagnosis"])}</div>'
        if rx.get("diagnosis")
        else ""
    )
    medicines = rx.get("medicines") or []
    not_recommended = rx.get("not_recommended") or []
    alternatives = rx.get("alternatives") or []
    non_pharm = rx.get("non_pharm") or []

    sections: list[str] = []
    if medicines:
        sections.append(
            f'<h3 class="subhead">Medicamentos prescritos</h3>{_render_med_table(medicines)}'
        )
    if not_recommended:
        sections.append(
            f'<h3 class="subhead">Revisión de seguridad</h3>{_render_med_table(not_recommended)}'
        )
    if not medicines and not not_recommended:
        sections.append(_empty("No requiere medicamentos."))
    if alternatives:
        sections.append(
            f'<h3 class="subhead">Alternativas terapéuticas</h3>{_render_med_table(alternatives)}'
        )
    if non_pharm:
        chips = "".join(f"<span>{_e(item)}</span>" for item in non_pharm)
        sections.append(
            f'<h3 class="subhead">Tratamientos no farmacológicos</h3><div class="nonpharm">{chips}</div>'
        )
    return diagnosis + "".join(sections)


def _render_recommendations(items: list[str]) -> str:
    if not items:
        return _empty("No se registraron recomendaciones adicionales.")
    lis = "".join(f"<li>{_text(item)}</li>" for item in items)
    return f'<ul class="rec-list">{lis}</ul>'


def render_report_html(model: dict) -> str:
    patient = model["patient"]
    encounter = model["encounter"]
    anamnesis = model["anamnesis"]
    symptoms = model["symptoms"]
    vitals = model["vitals"]
    triage = model.get("triage")
    labs = model.get("labs") or []
    confirmed = (model.get("diagnoses") or {}).get("confirmed") or []
    differential = (model.get("diagnoses") or {}).get("differential") or []

    doc_short = f"{patient['doc_type']} {patient['doc_number']}".strip()
    file_base = re.sub(r"[^a-zA-Z0-9]+", "-", f"historia-{patient['doc_number']}").strip("-").lower()

    encounter_stamp = encounter.get("date") or ""
    if encounter.get("start"):
        encounter_stamp = f"{encounter_stamp} · {encounter['start']}"

    meta_items = [
        ("Fecha de atención", encounter.get("date")),
        ("Inicio", encounter.get("start")),
        ("Cierre", encounter.get("end")),
        ("Médico tratante", encounter.get("doctor")),
        ("Institución", encounter.get("hospital")),
    ]
    meta_html = "".join(
        f'<div class="meta-item"><span class="meta-label">{_e(label)}</span>'
        f'<span class="meta-value">{_e(value) if value else "—"}</span></div>'
        for label, value in meta_items
    )

    patient_meta = []
    if patient.get("phone"):
        patient_meta.append(f'<span>Tel. <strong>{_e(patient["phone"])}</strong></span>')
    if patient.get("location"):
        patient_meta.append(f'<span>Residencia <strong>{_e(patient["location"])}</strong></span>')
    if patient.get("birth_date"):
        patient_meta.append(f'<span>Nacimiento <strong>{_e(patient["birth_date"])}</strong></span>')
    if patient.get("occupation"):
        patient_meta.append(f'<span>Ocupación <strong>{_e(patient["occupation"])}</strong></span>')

    age_chip = f'<span class="chip">{_e(patient["age"])} años</span>' if patient.get("age") else ""
    gender_chip = f'<span class="chip">{_e(patient["gender"])}</span>' if patient.get("gender") else ""

    symptoms_html = (
        '<div class="chip-list">'
        + "".join(f'<span class="symptom">{_e(item)}</span>' for item in symptoms)
        + "</div>"
        if symptoms
        else _empty("No se reportaron síntomas.")
    )

    anamnesis_body = f"""
    <div class="panel">
      <span class="panel-title">Motivo de consulta</span>
      <p class="reason">{_e(anamnesis.get('reason')) or 'Consulta clínica'}</p>
      <p class="narrative">{_text(anamnesis.get('evolution')) if anamnesis.get('evolution') else ''}</p>
    </div>
    <div class="panel soft">
      <span class="panel-title">Síntomas reportados</span>
      {symptoms_html}
    </div>"""

    vital_count = len(vitals)
    vitals_aside = f'<span class="sync-chip">{vital_count} constantes</span>' if vital_count else ""
    clinical_body = _render_vitals(vitals) + _render_triage(triage) + _render_labs(labs)

    diagnosis_aside = ""
    if confirmed:
        diagnosis_aside = f'<span class="sync-chip">{len(confirmed)} confirmado(s)</span>'
    elif differential:
        diagnosis_aside = f'<span class="sync-chip">{len(differential)} diferencial(es)</span>'

    notes = model.get("notes") or ""
    doctor = encounter.get("doctor") or "Médico tratante"
    signoff = f"""
    <div class="signoff">
      <div>
        <div class="sig-line"></div>
        <div class="sig-name">{_e(doctor)}</div>
        <div class="sig-role">Médico tratante · MIMETIC Clinical Suite</div>
        <div class="sig-license">Registro profesional no disponible en la demostración</div>
      </div>
      <div class="stamp">
        <span class="panel-title">Estado del documento</span>
        <div class="stamp-chips">
          <span class="stamp-chip">Borrador clínico</span>
          <span class="stamp-chip">Firma electrónica · roadmap</span>
          <span class="stamp-chip">Envío HIS · roadmap</span>
        </div>
        <p>Documento de demostración sin firma electrónica ni transmisión al HIS institucional. No constituye una receta válida.</p>
      </div>
    </div>"""

    recommendations = model.get("recommendations") or []

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Historia clínica · {_e(patient['name'])} · {_e(file_base)}</title>
<style>{_CSS}</style>
</head>
<body>
<div class="doc">

  <header class="masthead">
    <div class="brand">
      <div class="brand-mark">M</div>
      <div>
        <div class="brand-name">MIMETIC</div>
        <div class="brand-tag">Clinical Intelligence Suite</div>
      </div>
    </div>
    <div class="masthead-meta">
      <span class="eyebrow light">Historia clínica</span>
      <div class="masthead-title">Registro de atención</div>
      <div class="masthead-line">HC · <strong>{_e(patient['doc_number'])}</strong></div>
      <div class="masthead-line">{_e(encounter_stamp)}</div>
    </div>
  </header>

  <div class="syncbar">
    <span class="sync-dot"></span>
    <span>Documento clínico generado desde la sesión</span>
    <span class="spacer"></span>
    <span class="sync-chip mono">MIMETIC CORE v4.2</span>
    <span class="sync-chip demo">Demostración</span>
  </div>

  <section class="patient-card">
    <div class="patient-main">
      <div class="avatar">{_e(patient['initials'])}</div>
      <div>
        <span class="eyebrow">Paciente</span>
        <h1 class="patient-name">{_e(patient['name'])}</h1>
        <div class="chips">
          <span class="chip chip-id mono">{_e(doc_short)}</span>
          {age_chip}
          {gender_chip}
        </div>
        <div class="patient-meta">{''.join(patient_meta)}</div>
      </div>
    </div>
    <div class="patient-side">{meta_html}</div>
  </section>

  {_section("01", "Anamnesis", "Motivo de consulta y síntomas", anamnesis_body)}
  {_section("02", "Antecedentes", "Perfil clínico y factores de riesgo", _render_background(model['background']))}
  {_section("03", "Examen físico", "Signos vitales, triaje y laboratorio", clinical_body, vitals_aside)}
  {_section("04", "Impresión diagnóstica", "Diagnósticos y diferenciales", _render_diagnoses(model['diagnoses']), diagnosis_aside)}
  {_section("05", "Plan farmacológico", "Prescripción y seguridad del medicamento", _render_prescription(model.get('prescription')))}
  {_section("06", "Indicaciones", "Recomendaciones médicas", _render_recommendations(recommendations))}

  <section class="section">
    <div class="section-head">
      <span class="section-num">07</span>
      <div class="section-title">
        <span class="eyebrow">Observaciones</span>
        <h2>Nota clínica del médico</h2>
      </div>
    </div>
    {f'<div class="note-card">{_text(notes)}</div>' if notes else _empty('Sin observaciones registradas por el médico.')}
  </section>

  {signoff}

  <footer class="legal">
    <div class="legal-top">
      <span class="legal-brand">MIMETIC · Historia clínica digital</span>
      <span class="legal-meta">{_e(file_base)} · {_e(encounter['generated_date'])}</span>
    </div>
    <p>Este documento es generado por MIMETIC como herramienta de apoyo al diagnóstico y no sustituye el criterio de un profesional de la salud. Los datos corresponden a una demostración; la firma electrónica, el envío al HIS y la validación de interoperabilidad están en roadmap.</p>
    <p>Ley 23 de 1981 — Colombia. Documento confidencial de uso clínico.</p>
  </footer>

</div>
</body>
</html>"""
