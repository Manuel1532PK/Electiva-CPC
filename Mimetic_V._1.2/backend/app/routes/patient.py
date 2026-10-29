from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.auth.permissions import require_roles

router = APIRouter()

# All patient fields organized by section
PATIENT_FIELD_GROUPS = [
    {
        "section": "Identificación del Paciente",
        "fields": [
            {"key": "name", "label": "Nombre completo"},
            {"key": "document_type", "label": "Tipo de documento"},
            {"key": "id_document", "label": "Número de documento"},
            {"key": "birth_date", "label": "Fecha de nacimiento"},
            {"key": "age", "label": "Edad"},
            {"key": "gender", "label": "Género"},
            {"key": "occupation", "label": "Ocupación"},
            {"key": "phone", "label": "Teléfono"},
            {"key": "location", "label": "Ciudad de residencia"},
        ],
    },
    {
        "section": "Anamnesis",
        "fields": [
            {"key": "consultation_reason", "label": "Motivo de consulta"},
            {"key": "symptom_evolution", "label": "Tiempo de evolución"},
        ],
    },
    {
        "section": "Antecedentes Personales",
        "fields": [
            {"key": "tobacco", "label": "Consumo de tabaco en los últimos 3 meses"},
            {"key": "alcohol", "label": "Consumo de alcohol en el último mes"},
            {"key": "substances", "label": "Uso de sustancias en el último año"},
            {"key": "physical_activity", "label": "Actividad física en el último mes"},
            {"key": "medical_history", "label": "Antecedentes médicos"},
            {"key": "surgical_history", "label": "Antecedentes quirúrgicos"},
            {"key": "pharmacological_history", "label": "Antecedentes farmacológicos"},
            {"key": "allergies", "label": "Alergias conocidas"},
        ],
    },
    {
        "section": "Signos Vitales",
        "fields": [
            {"key": "blood_pressure", "label": "Presión arterial (mmHg)"},
            {"key": "heart_rate", "label": "Frecuencia cardíaca (lpm)"},
            {"key": "respiratory_rate", "label": "Frecuencia respiratoria (rpm)"},
            {"key": "temperature", "label": "Temperatura (°C)"},
            {"key": "weight", "label": "Peso (kg)"},
            {"key": "height", "label": "Estatura (cm)"},
        ],
    },
]

# Flat list for backwards compat and missing field checking
PATIENT_FIELDS = [f for g in PATIENT_FIELD_GROUPS for f in g["fields"]]

OPTIONAL_FIELDS = {
    "tobacco", "alcohol", "substances", "physical_activity",
    "medical_history", "surgical_history", "pharmacological_history",
    "allergies", "consultation_reason", "symptom_evolution",
    "occupation", "phone", "birth_date", "document_type",
    "gender", "blood_pressure", "heart_rate", "respiratory_rate",
    "temperature",
}


class PatientInfoRequest(BaseModel):
    patient_info: dict = {}
    message: str = ""


class PatientInfoResponse(BaseModel):
    reply: str
    patient_info: dict
    missing_fields: list[str]
    complete: bool
    field_groups: list | None = None


@router.post("/patient", response_model=PatientInfoResponse)
async def patient_info(
    request: PatientInfoRequest,
    current_user=Depends(require_roles("medico", "admin", "super_admin")),
):
    info = dict(request.patient_info)
    msg = request.message.strip()

    if msg:
        msg_lower = msg.lower()
        neg_keywords = ("ninguno", "no", "none", "ninguna", "no aplica", "n/a", "no fuma", "no bebe", "sedentario", "activo")

        # Negation keywords only fill optional fields
        if msg_lower in neg_keywords:
            for field in PATIENT_FIELDS:
                key = field["key"]
                if key in OPTIONAL_FIELDS and (key not in info or not info[key]):
                    info[key] = msg
                    break
        # Normal answers prioritize required fields, then optional
        else:
            target = None
            for field in PATIENT_FIELDS:
                key = field["key"]
                if key not in info or not info[key]:
                    if key in OPTIONAL_FIELDS:
                        if target is None:
                            target = field
                    else:
                        target = field
                        break
            if target:
                info[target["key"]] = msg

    missing = []
    for field in PATIENT_FIELDS:
        key = field["key"]
        if key in OPTIONAL_FIELDS:
            continue
        if key not in info or not info[key]:
            missing.append(key)

    if not missing:
        return PatientInfoResponse(
            reply="Paciente registrado correctamente. Ahora describe los síntomas que presenta.",
            patient_info=info,
            missing_fields=[],
            complete=True,
            field_groups=PATIENT_FIELD_GROUPS,
        )

    next_field = None
    for field in PATIENT_FIELDS:
        if field["key"] in missing:
            next_field = field
            break

    reply = next_field["label"] if next_field else "Todos los datos están registrados."

    return PatientInfoResponse(
        reply=reply,
        patient_info=info,
        missing_fields=missing,
        complete=False,
        field_groups=PATIENT_FIELD_GROUPS,
    )
