"""
MIMETIC - Datos de prueba (demo) para validar el sistema de punta a punta.

Crea de forma idempotente:
  - Hospital DEMO-001
  - Usuarios medico / admin / pacientes con contrasena Mimetic123!
  - 3 historias clinicas con 7 sesiones reales (signos vitales, sintomas,
    diagnosticos del motor experto, tratamiento y reporte HTML)
  - Sesiones marcadas con demo_seed=True (se pueden borrar sin tocar datos reales)

Uso (desde la carpeta backend, con el venv):
    .venv\\Scripts\\python.exe seed_demo.py

Requiere MongoDB local en 127.0.0.1:27017 y la base de conocimiento ya sembrada
(el backend la siembra automaticamente al arrancar).
"""

import asyncio
import os
import sys
from datetime import datetime

# El MongoDB nativo de Windows escucha en 127.0.0.1; el contenedor Docker puede
# quedar en ::1 y no contiene los datos reales. Forzamos la instancia correcta.
os.environ.setdefault("MONGODB_URL", "mongodb://127.0.0.1:27017")

from bson import ObjectId
from passlib.context import CryptContext

from app.database.mongodb import connect_db, close_db, get_db
from app.expert_system.engine import diagnose, recommend_treatment
from app.routes.report import ReportRequest, generate_report

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PASSWORD = "Mimetic123!"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

HOSPITAL = {
    "code": "DEMO-001",
    "name": "Hospital Demo MIMETIC",
    "address": "Calle 100 # 15-20, Bogota",
    "phone": "+57 601 555 0100",
    "email": "contacto@hospitaldemo.local",
}

# ── Usuarios ─────────────────────────────────────────────────────

USERS = [
    {
        "email": "dra.rios@mimetic.local",
        "name": "Valeria Rios",
        "role": "medico",
        "first_name": "Valeria",
        "last_name": "Rios",
        "document_type": "CC",
        "document_number": "900123456",
        "birth_date": "1985-02-17",
        "country": "Colombia",
        "department": "Cundinamarca",
        "city": "Bogota",
        "phone": "+57 310 555 0101",
    },
    {
        "email": "admin@mimetic.local",
        "name": "Admin Demo MIMETIC",
        "role": "admin",
        "first_name": "Admin",
        "last_name": "Demo",
        "document_type": "CC",
        "document_number": "900999999",
        "birth_date": "1980-01-01",
        "country": "Colombia",
        "department": "Cundinamarca",
        "city": "Bogota",
        "phone": "+57 310 555 0102",
    },
    {
        "email": "paciente@mimetic.local",
        "name": "Carlos Andres Mendoza Rojas",
        "role": "paciente",
        "first_name": "Carlos Andres",
        "last_name": "Mendoza Rojas",
        "document_type": "CC",
        "document_number": "1020304050",
        "birth_date": "1987-04-12",
        "country": "Colombia",
        "department": "Cundinamarca",
        "city": "Bogota",
        "phone": "+57 310 555 0142",
    },
    {
        "email": "maria@mimetic.local",
        "name": "Maria Fernanda Lopez Gomez",
        "role": "paciente",
        "first_name": "Maria Fernanda",
        "last_name": "Lopez Gomez",
        "document_type": "CC",
        "document_number": "1098765432",
        "birth_date": "1994-09-23",
        "country": "Colombia",
        "department": "Antioquia",
        "city": "Medellin",
        "phone": "+57 320 555 0198",
    },
    {
        "email": "andres@mimetic.local",
        "name": "Andres Felipe Ramirez Torres",
        "role": "paciente",
        "first_name": "Andres Felipe",
        "last_name": "Ramirez Torres",
        "document_type": "CC",
        "document_number": "1000000001",
        "birth_date": "1958-01-30",
        "country": "Colombia",
        "department": "Valle del Cauca",
        "city": "Cali",
        "phone": "+57 315 555 0177",
    },
]

# ── Pacientes, historias y sesiones ──────────────────────────────

PATIENTS = [
    {
        "document_number": "1020304050",
        "document_type": "CC",
        "first_name": "Carlos Andres",
        "last_name": "Mendoza Rojas",
        "birth_date": "1987-04-12",
        "age": "39",
        "gender": "Masculino",
        "occupation": "Conductor de reparto",
        "phone": "+57 310 555 0142",
        "country": "Colombia",
        "department": "Cundinamarca",
        "city": "Bogota",
        "history_created_at": datetime(2026, 8, 14, 15, 0),
        "sessions": [
            {
                "id": "66d000000000000000000001",
                "date": datetime(2026, 8, 14, 15, 20),
                "consultation_start": "03:20 PM",
                "consultation_reason": "Fiebre y dolor de cabeza de 4 dias de evolucion",
                "symptom_evolution": (
                    "Inicia hace 4 dias con fiebre alta, dolor de cabeza y dolor detras de los ojos. "
                    "En las ultimas 24 horas presenta nausea y dolor muscular generalizado. "
                    "Niega sangrado de encias o petequias."
                ),
                "tobacco": "No",
                "alcohol": "Ocasional",
                "substances": "No",
                "physical_activity": "Sedentario",
                "pregnancy": "No",
                "medical_history": "Sin antecedentes cronicos conocidos",
                "surgical_history": "Ninguna",
                "pharmacological_history": "Ninguno",
                "allergies": "Ninguna",
                "vitals": {
                    "blood_pressure": "118/76",
                    "heart_rate": "96",
                    "respiratory_rate": "20",
                    "temperature": "38.9",
                    "weight": "82",
                    "height": "176",
                },
                "symptoms": [
                    "fiebre alta persistente",
                    "dolor de cabeza",
                    "dolor muscular",
                    "dolor detrás de los ojos",
                    "náuseas",
                ],
                "diagnosis": "dengue",
                "doctor_notes": (
                    "Paciente con criterios clinicos de dengue sin signos de alarma. "
                    "Se solicita hemograma, prueba NS1 y control en 48 horas. "
                    "Se indica hidratacion abundante y acetaminofen."
                ),
            },
            {
                "id": "66d000000000000000000002",
                "date": datetime(2026, 9, 21, 9, 40),
                "consultation_start": "09:40 AM",
                "consultation_reason": "Tos y congestion nasal de 3 dias",
                "symptom_evolution": (
                    "Cuadro de 3 dias con tos seca, congestion nasal, dolor de garganta y fiebre "
                    "de 38 grados. Refiere malestar general y dolor muscular."
                ),
                "tobacco": "No",
                "alcohol": "Ocasional",
                "substances": "No",
                "physical_activity": "Sedentario",
                "pregnancy": "No",
                "medical_history": "Sin antecedentes cronicos conocidos",
                "surgical_history": "Ninguna",
                "pharmacological_history": "Ninguno",
                "allergies": "Ninguna",
                "vitals": {
                    "blood_pressure": "120/78",
                    "heart_rate": "88",
                    "respiratory_rate": "18",
                    "temperature": "38.1",
                    "weight": "81",
                    "height": "176",
                },
                "symptoms": [
                    "tos",
                    "congestión nasal",
                    "dolor de garganta",
                    "fiebre",
                    "malestar general intenso",
                    "dolor muscular",
                ],
                "diagnosis": "influenza (gripe)",
                "doctor_notes": (
                    "Cuadro compatible con influenza. Reposo, hidratacion y manejo sintomatico. "
                    "Se recomienda aislamiento respiratorio por 5 dias."
                ),
            },
            {
                "id": "66d000000000000000000003",
                "date": datetime(2026, 10, 19, 18, 5),
                "consultation_start": "06:05 PM",
                "consultation_reason": "Dolor abdominal y diarrea de 24 horas",
                "symptom_evolution": (
                    "Desde ayer presenta deposiciones liquidas (6 en 24 horas), dolor abdominal "
                    "tipo colico, nausea y fiebre de 37.9 grados. Refiere haber comido en un puesto callejero."
                ),
                "tobacco": "No",
                "alcohol": "Ocasional",
                "substances": "No",
                "physical_activity": "Sedentario",
                "pregnancy": "No",
                "medical_history": "Sin antecedentes cronicos conocidos",
                "surgical_history": "Ninguna",
                "pharmacological_history": "Ninguno",
                "allergies": "Ninguna",
                "vitals": {
                    "blood_pressure": "110/70",
                    "heart_rate": "92",
                    "respiratory_rate": "18",
                    "temperature": "37.9",
                    "oxygen_saturation": "96",
                    "weight": "80",
                    "height": "176",
                },
                "context": {
                    "triage_level": 3,
                    "triage_system": "Manchester",
                    "triage_score": "NEWS2 = 2 · CURB-65 = 0",
                    "triage_discriminators": "Diarrea con deshidratacion leve, fiebre 37.9 C y taquicardia leve.",
                    "labs": {
                        "pao2": "92",
                        "lactate": "1.8",
                        "leukocytes": "11.4",
                        "creatinine": "0.9",
                        "crp": "28",
                    },
                },
                "symptoms": [
                    "diarrea",
                    "dolor abdominal",
                    "náuseas",
                    "fiebre",
                    "pérdida de apetito",
                ],
                "diagnosis": "gastroenteritis aguda",
                "doctor_notes": (
                    "Gastroenteritis aguda de probable origen alimentario. Sin signos de deshidratacion "
                    "severa. Se indica suero oral, dieta blanda y signos de alarma."
                ),
            },
        ],
    },
    {
        "document_number": "1098765432",
        "document_type": "CC",
        "first_name": "Maria Fernanda",
        "last_name": "Lopez Gomez",
        "birth_date": "1994-09-23",
        "age": "31",
        "gender": "Femenino",
        "occupation": "Disenadora grafica",
        "phone": "+57 320 555 0198",
        "country": "Colombia",
        "department": "Antioquia",
        "city": "Medellin",
        "history_created_at": datetime(2026, 7, 3, 10, 45),
        "sessions": [
            {
                "id": "66d000000000000000000011",
                "date": datetime(2026, 7, 3, 11, 10),
                "consultation_start": "11:10 AM",
                "consultation_reason": "Cefalea intensa unilateral de 12 horas",
                "symptom_evolution": (
                    "Dolor pulsatil en region temporal derecha de 12 horas, asociado a fotofobia, "
                    "fonofobia y nausea. Precedido de vision de luces intermitentes. "
                    "Refiere episodios similares en los ultimos meses."
                ),
                "tobacco": "No",
                "alcohol": "Ocasional",
                "substances": "No",
                "physical_activity": "Moderada",
                "pregnancy": "No",
                "medical_history": "Migrana episodica en seguimiento",
                "surgical_history": "Ninguna",
                "pharmacological_history": "Ibuprofeno ocasional",
                "allergies": "Ninguna",
                "vitals": {
                    "blood_pressure": "115/72",
                    "heart_rate": "74",
                    "respiratory_rate": "16",
                    "temperature": "36.7",
                    "weight": "60",
                    "height": "165",
                },
                "symptoms": [
                    "dolor de cabeza pulsátil unilateral",
                    "fotofobia",
                    "fonofobia",
                    "náuseas",
                    "aura visual",
                ],
                "diagnosis": "migrana",
                "doctor_notes": (
                    "Migrana con aura. Se indica tratamiento abortivo en fase temprana, "
                    "diario de cefaleas y control por consulta externa."
                ),
            },
            {
                "id": "66d000000000000000000012",
                "date": datetime(2026, 9, 28, 16, 30),
                "consultation_start": "04:30 PM",
                "consultation_reason": "Ardor al orinar y dolor lumbar de 2 dias",
                "symptom_evolution": (
                    "Desde hace 2 dias presenta ardor al orinar, aumento de la frecuencia urinaria, "
                    "urgencia y dolor lumbar bilateral. Orina turbia y fiebre de 37.8 grados."
                ),
                "tobacco": "No",
                "alcohol": "Ocasional",
                "substances": "No",
                "physical_activity": "Moderada",
                "pregnancy": "No",
                "medical_history": "Infeccion urinaria previa hace 2 anos",
                "surgical_history": "Ninguna",
                "pharmacological_history": "Ninguno",
                "allergies": "Ninguna",
                "vitals": {
                    "blood_pressure": "108/68",
                    "heart_rate": "84",
                    "respiratory_rate": "17",
                    "temperature": "37.8",
                    "oxygen_saturation": "97",
                    "weight": "59",
                    "height": "165",
                },
                "context": {
                    "triage_level": 3,
                    "triage_system": "Manchester",
                    "triage_score": "NEWS2 = 1 · qSOFA = 0",
                    "triage_discriminators": "Disuria, fiebre 37.8 C y dolor lumbar bilateral sin signos de sepsis.",
                    "labs": {
                        "pao2": "95",
                        "lactate": "1.2",
                        "leukocytes": "12.8",
                        "creatinine": "0.8",
                        "crp": "46",
                    },
                },
                "symptoms": [
                    "ardor al orinar",
                    "frecuencia urinaria",
                    "urgencia urinaria",
                    "dolor lumbar",
                    "fiebre",
                    "orina turbia",
                ],
                "diagnosis": "infeccion urinaria",
                "doctor_notes": (
                    "Infeccion urinaria baja no complicada. Se solicita uroanalisis y urocultivo. "
                    "Se inicia antibiotico empirico y se indica aumentar ingesta de liquidos."
                ),
            },
        ],
    },
    {
        "document_number": "1000000001",
        "document_type": "CC",
        "first_name": "Andres Felipe",
        "last_name": "Ramirez Torres",
        "birth_date": "1958-01-30",
        "age": "68",
        "gender": "Masculino",
        "occupation": "Pensionado (exdocente)",
        "phone": "+57 315 555 0177",
        "country": "Colombia",
        "department": "Valle del Cauca",
        "city": "Cali",
        "history_created_at": datetime(2026, 6, 11, 3, 50),
        "sessions": [
            {
                "id": "66d000000000000000000021",
                "date": datetime(2026, 6, 11, 4, 15),
                "consultation_start": "04:15 AM",
                "consultation_reason": "Dolor toracico opresivo de 40 minutos",
                "symptom_evolution": (
                    "Dolor retroesternal opresivo de 40 minutos, irradiado a brazo izquierdo, "
                    "asociado a disnea, sudoracion profusa y nausea. Sintomas iniciaron en reposo. "
                    "Antecedente de hipertension y dislipidemia."
                ),
                "tobacco": "Si, 30 anos (10 cigarrillos/dia)",
                "alcohol": "Ocasional",
                "substances": "No",
                "physical_activity": "Leve",
                "pregnancy": "No",
                "medical_history": "Hipertension arterial, dislipidemia",
                "surgical_history": "Apendicectomia en 1990",
                "pharmacological_history": "Losartan 50 mg/dia, atorvastatina 20 mg/dia",
                "allergies": "Ninguna",
                "vitals": {
                    "blood_pressure": "150/95",
                    "heart_rate": "104",
                    "respiratory_rate": "24",
                    "temperature": "36.5",
                    "weight": "78",
                    "height": "170",
                },
                "symptoms": [
                    "dolor torácico opresivo",
                    "dolor irradiado a brazo izquierdo",
                    "disnea",
                    "sudoración profusa",
                    "náuseas",
                ],
                "diagnosis": "infarto agudo de miocardio",
                "doctor_notes": (
                    "Sindrome coronario agudo con elevacion del ST en cara inferior. "
                    "Se activa codigo infarto, se administra aspirina y se traslada a unidad "
                    "de hemodinamia para angioplastia primaria."
                ),
            },
            {
                "id": "66d000000000000000000022",
                "date": datetime(2026, 10, 2, 10, 0),
                "consultation_start": "10:00 AM",
                "consultation_reason": "Control de hipertension y cefalea occipital",
                "symptom_evolution": (
                    "En control posterior a evento coronario. Refiere cefalea occipital matutina, "
                    "vertigo leve, vision borrosa transitoria y zumbido de oidos. "
                    "No adherencia completa al tratamiento antihipertensivo."
                ),
                "tobacco": "Si, 30 anos (10 cigarrillos/dia)",
                "alcohol": "Ocasional",
                "substances": "No",
                "physical_activity": "Leve",
                "pregnancy": "No",
                "medical_history": "Hipertension arterial, dislipidemia, infarto agudo de miocardio (junio 2026)",
                "surgical_history": "Apendicectomia en 1990, angioplastia coronaria en 2026",
                "pharmacological_history": "Losartan 50 mg/dia, atorvastatina 20 mg/dia, aspirina 100 mg/dia",
                "allergies": "Ninguna",
                "vitals": {
                    "blood_pressure": "158/98",
                    "heart_rate": "88",
                    "respiratory_rate": "18",
                    "temperature": "36.6",
                    "oxygen_saturation": "95",
                    "weight": "79",
                    "height": "170",
                },
                "context": {
                    "triage_level": 3,
                    "triage_system": "ESI",
                    "triage_score": "NEWS2 = 3 · riesgo cardiovascular alto",
                    "triage_discriminators": "Cefalea occipital, cifras tensionales elevadas y antecedente de IAM reciente.",
                    "labs": {
                        "pao2": "88",
                        "lactate": "1.5",
                        "leukocytes": "8.2",
                        "creatinine": "1.3",
                        "crp": "12",
                    },
                },
                "symptoms": [
                    "dolor de cabeza occipital",
                    "vértigo",
                    "visión borrosa",
                    "zumbido de oídos",
                ],
                "diagnosis": "hipertension arterial",
                "doctor_notes": (
                    "Hipertension no controlada. Se refuerza adherencia, se solicita MAPA de 24 horas "
                    "y perfil lipidico. Se ajusta losartan y se indica control en 2 semanas."
                ),
            },
        ],
    },
]


def build_patient_info(patient: dict, session: dict) -> dict:
    """patient_info con la forma exacta que espera el flujo del medico."""
    return {
        "first_name": patient["first_name"],
        "last_name": patient["last_name"],
        "name": f"{patient['first_name']} {patient['last_name']}",
        "document_type": patient["document_type"],
        "id_document": patient["document_number"],
        "document_number": patient["document_number"],
        "birth_date": patient["birth_date"],
        "age": patient["age"],
        "gender": patient["gender"],
        "occupation": patient["occupation"],
        "phone": patient["phone"],
        "country": patient["country"],
        "department": patient["department"],
        "city": patient["city"],
        "location": f"{patient['city']}, {patient['department']}",
        "consultation_reason": session["consultation_reason"],
        "symptom_evolution": session["symptom_evolution"],
        "tobacco": session["tobacco"],
        "alcohol": session["alcohol"],
        "substances": session["substances"],
        "physical_activity": session["physical_activity"],
        "pregnancy": session["pregnancy"],
        "medical_history": session["medical_history"],
        "surgical_history": session["surgical_history"],
        "pharmacological_history": session["pharmacological_history"],
        "allergies": session["allergies"],
        "consultation_start": session["consultation_start"],
        **session["vitals"],
        "triage_level": (session.get("context") or {}).get("triage_level", ""),
        "triage_system": (session.get("context") or {}).get("triage_system", ""),
        "triage_score": (session.get("context") or {}).get("triage_score", ""),
        "triage_discriminators": (session.get("context") or {}).get("triage_discriminators", ""),
        "lab_pao2": ((session.get("context") or {}).get("labs") or {}).get("pao2", ""),
        "lab_lactate": ((session.get("context") or {}).get("labs") or {}).get("lactate", ""),
        "lab_leukocytes": ((session.get("context") or {}).get("labs") or {}).get("leukocytes", ""),
        "lab_creatinine": ((session.get("context") or {}).get("labs") or {}).get("creatinine", ""),
        "lab_crp": ((session.get("context") or {}).get("labs") or {}).get("crp", ""),
    }


async def upsert_hospital(db) -> dict:
    now = datetime.utcnow()
    await db.hospitals.update_one(
        {"code": HOSPITAL["code"]},
        {
            "$set": {
                "name": HOSPITAL["name"],
                "address": HOSPITAL["address"],
                "phone": HOSPITAL["phone"],
                "email": HOSPITAL["email"],
                "active": True,
            },
            "$setOnInsert": {"created_at": now},
        },
        upsert=True,
    )
    hospital = await db.hospitals.find_one({"code": HOSPITAL["code"]})
    print(f"[OK] Hospital {hospital['name']} ({hospital['code']}) id={hospital['_id']}")
    return hospital


async def upsert_users(db, hospital_id: str) -> dict[str, dict]:
    now = datetime.utcnow()
    password_hash = pwd_context.hash(PASSWORD)
    users: dict[str, dict] = {}
    for data in USERS:
        update = {
            "name": data["name"],
            "password_hash": password_hash,
            "role": data["role"],
            "hospital_id": hospital_id if data["role"] != "super_admin" else "",
            "first_name": data["first_name"],
            "last_name": data["last_name"],
            "document_type": data["document_type"],
            "document_number": data["document_number"],
            "birth_date": data["birth_date"],
            "country": data["country"],
            "department": data["department"],
            "city": data["city"],
            "phone": data["phone"],
            "verified": True,
            "active": True,
        }
        await db.users.update_one(
            {"email": data["email"]},
            {"$set": update, "$setOnInsert": {"created_at": now}},
            upsert=True,
        )
        user = await db.users.find_one({"email": data["email"]})
        users[data["email"]] = user
        print(f"[OK] Usuario {data['email']:<28} rol={data['role']:<8} doc={data['document_number']}")
    return users


async def upsert_history(db, patient: dict) -> None:
    now = datetime.utcnow()
    await db.clinical_histories.update_one(
        {"document_number": patient["document_number"]},
        {
            "$set": {
                "document_type": patient["document_type"],
                "first_name": patient["first_name"],
                "last_name": patient["last_name"],
                "birth_date": patient["birth_date"],
                "age": patient["age"],
                "gender": patient["gender"],
                "occupation": patient["occupation"],
                "phone": patient["phone"],
                "country": patient["country"],
                "department": patient["department"],
                "city": patient["city"],
                "updated_at": patient["sessions"][-1]["date"],
                "demo_seed": True,
            },
            "$setOnInsert": {"created_at": patient["history_created_at"]},
        },
        upsert=True,
    )


async def seed_sessions(db, patient: dict, doctor: dict, hospital: dict) -> None:
    for session in patient["sessions"]:
        patient_info = build_patient_info(patient, session)

        # Medicamentos sugeridos (seleccionados por el medico en el reporte)
        treatment = await recommend_treatment(session["diagnosis"], patient_info)
        selected = [m.get("name") for m in (treatment or {}).get("available", []) if m.get("name")]

        session_doc = {
            "_id": ObjectId(session["id"]),
            "document_number": patient["document_number"],
            "doctor_id": str(doctor["_id"]),
            "doctor_name": doctor["name"],
            "hospital_id": str(hospital["_id"]),
            "hospital_name": hospital["name"],
            "date": session["date"],
            "consultation_reason": session["consultation_reason"],
            "symptom_evolution": session["symptom_evolution"],
            "tobacco": session["tobacco"],
            "alcohol": session["alcohol"],
            "substances": session["substances"],
            "physical_activity": session["physical_activity"],
            "pregnancy": session["pregnancy"],
            "medical_history": session["medical_history"],
            "surgical_history": session["surgical_history"],
            "pharmacological_history": session["pharmacological_history"],
            "allergies": session["allergies"],
            "blood_pressure": session["vitals"]["blood_pressure"],
            "heart_rate": session["vitals"]["heart_rate"],
            "respiratory_rate": session["vitals"]["respiratory_rate"],
            "temperature": session["vitals"]["temperature"],
            "oxygen_saturation": session["vitals"].get("oxygen_saturation", ""),
            "weight": session["vitals"]["weight"],
            "height": session["vitals"]["height"],
            "triage_level": (session.get("context") or {}).get("triage_level", 0),
            "triage_system": (session.get("context") or {}).get("triage_system", ""),
            "triage_discriminators": (session.get("context") or {}).get("triage_discriminators", ""),
            "triage_score": (session.get("context") or {}).get("triage_score", ""),
            "labs": (session.get("context") or {}).get("labs", {}),
            "symptoms": session["symptoms"],
            "diagnoses": [],
            "treatment": None,
            "report_html": "",
            "doctor_review": None,
            "demo_seed": True,
            "created_at": session["date"],
        }

        # Diagnostico real del motor experto (no inventado a mano)
        session_doc["diagnoses"] = await diagnose(session["symptoms"], patient_info=patient_info)

        await db.sessions.insert_one(session_doc)

        doctor_review = {
            "confirmedDiagnoses": [session["diagnosis"]],
            "rejectedDiagnoses": [],
            "manualDiagnoses": [],
            "selectedMedicines": selected,
            "modifiedDoses": {},
            "doctorNotes": session["doctor_notes"],
        }

        # Reporte HTML real usando el mismo endpoint de la aplicacion
        request = ReportRequest(
            patient_info=patient_info,
            symptoms=session["symptoms"],
            selected_diagnosis=session["diagnosis"],
            doctor_review=doctor_review,
            session_id=session["id"],
            document_number=patient["document_number"],
        )
        result = await generate_report(request)

        # generate_report solo actualiza symptoms/diagnoses/treatment/report_html/doctor_review
        await db.sessions.update_one(
            {"_id": ObjectId(session["id"])},
            {"$set": {"date": session["date"]}},
        )

        top = session_doc["diagnoses"][0] if session_doc["diagnoses"] else {}
        print(
            f"  [OK] {session['date']:%Y-%m-%d} {patient['first_name']} {patient['last_name']} "
            f"-> {session['diagnosis']} "
            f"(IA: {top.get('disease_name', 'n/a')} {top.get('confidence', 0):.0%}) "
            f"reporte={len(result.html_report)} chars"
        )


async def main() -> int:
    print("MIMETIC - Sembrando datos de prueba\n")

    if not await connect_db():
        print("[ERROR] No se pudo conectar a MongoDB. Verifica que mongod escuche en 127.0.0.1:27017.")
        return 1

    db = get_db()
    seed_data = await db.diseases.count_documents({})
    if seed_data == 0:
        print("[ERROR] La base de conocimiento esta vacia. Inicia el backend una vez para sembrarla.")
        await close_db()
        return 1

    hospital = await upsert_hospital(db)
    users = await upsert_users(db, str(hospital["_id"]))
    doctor = users["dra.rios@mimetic.local"]

    print()
    # Idempotencia: borra solo las sesiones de demo, nunca las reales.
    deleted = await db.sessions.delete_many({"demo_seed": True})
    if deleted.deleted_count:
        print(f"[OK] Sesiones demo anteriores eliminadas: {deleted.deleted_count}\n")

    total_sessions = 0
    for patient in PATIENTS:
        await upsert_history(db, patient)
        await seed_sessions(db, patient, doctor, hospital)
        total_sessions += len(patient["sessions"])
        print()

    # La fecha de actualizacion de la historia debe reflejar la ultima sesion.
    for patient in PATIENTS:
        await db.clinical_histories.update_one(
            {"document_number": patient["document_number"]},
            {"$set": {"updated_at": patient["sessions"][-1]["date"]}},
        )

    print("=" * 74)
    print("DATOS DE PRUEBA LISTOS")
    print("=" * 74)
    print(f"Historias clinicas : {await db.clinical_histories.count_documents({'demo_seed': True})}")
    print(f"Sesiones demo      : {await db.sessions.count_documents({'demo_seed': True})} (esperadas {total_sessions})")
    print()
    print(f"Contrasena para todos: {PASSWORD}")
    print()
    print("MEDICO (panel clinico / chatbot):")
    print("  dra.rios@mimetic.local     Dra. Valeria Rios")
    print("  medico@mimetic.local       (cuenta existente)")
    print()
    print("ADMIN:")
    print("  admin@mimetic.local")
    print()
    print("PACIENTES (portal del paciente):")
    print("  paciente@mimetic.local     CC 1020304050  Carlos Andres Mendoza (3 sesiones)")
    print("  maria@mimetic.local        CC 1098765432  Maria Fernanda Lopez (2 sesiones)")
    print("  andres@mimetic.local       CC 1000000001  Andres Felipe Ramirez (2 sesiones)")
    print()
    print("Busca estos documentos en el panel del medico: 1020304050, 1098765432, 1000000001")
    print("=" * 74)

    await close_db()
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
