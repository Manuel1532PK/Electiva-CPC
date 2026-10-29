# MIMETIC IA · Versión 1.2

Copia limpia y ejecutable del proyecto con el rediseño de **login**, **espacio de IA**,
**historial clínico** y **documentos PDF** (reporte por atención + historia consolidada).

Fecha de corte: **25 de octubre de 2026**.

## Qué incluye esta versión

| Área | Estado en V1.2 |
|------|----------------|
| Login y sesión | Rediseño Stitch/MIMETIC, JWT real, roles y estado de conexión/latencia |
| Espacio de IA | Chat clínico, panel de contexto del paciente, comandos `/triaje`, `/lab`, `/fhir`, `/listo`, dictado simulado |
| Historias clínicas | Búsqueda por documento, actividad reciente, línea de tiempo por paciente |
| Documento por atención | `report_html` persistido en MongoDB y regenerable |
| Historia consolidada | Generada en el navegador con todas las atenciones del paciente |
| PDF | Diálogo de impresión del navegador ("Guardar como PDF"), sin dependencias nuevas |
| FHIR R4 | Exportación **simulada** en pestaña aparte; no valida ni envía a un HIS |

## Requisitos

- Python **3.11+**
- Node.js **20+** y npm
- MongoDB local (servicio nativo en `127.0.0.1:27017`) o MongoDB Atlas

## Arranque local

```powershell
# 1. MongoDB (si no lo tienes como servicio de Windows)
docker compose up -d mongodb

# 2. Backend (puerto 8001)
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env    # ajusta MONGODB_URL y JWT_SECRET
uvicorn main:app --port 8001 --reload

# 3. Frontend (puerto 5173, en otra terminal)
cd frontend
npm install
npm run dev
```

Abre **http://127.0.0.1:5173**. El proxy de Vite envía `/api` y `/health` a
`http://127.0.0.1:8001`.

### Datos de demostración

Con el backend arrancado al menos una vez (crea el catálogo de conocimiento):

```powershell
cd backend
python seed_demo.py
```

Crea 3 pacientes, 7 atenciones y sus documentos. Credenciales en
[`DATOS_PRUEBA.md`](./DATOS_PRUEBA.md) (contraseña `Mimetic123!`).

### Regenerar los documentos guardados

Si cambias la plantilla del reporte, actualiza los `report_html` existentes sin tocar
los datos clínicos:

```powershell
cd backend
python regenerate_reports.py            # aplica cambios
python regenerate_reports.py --dry-run  # solo muestra el alcance
```

## Estructura

```
Mimetic V. 1.2/
├── backend/
│   ├── app/
│   │   ├── auth/            # JWT, permisos y RBAC
│   │   ├── database/        # Motor async, reconexión, ping real
│   │   ├── expert_system/   # Motor de diagnóstico y conversación
│   │   ├── models/          # Pydantic (usuario, historia clínica, catálogo)
│   │   ├── reports/         # Plantilla print-first del documento clínico
│   │   └── routes/          # auth, diagnose, clinical_history, report, ...
│   ├── tests/               # pytest
│   ├── main.py              # App FastAPI, CORS, rate limit, auto-seed, /health
│   ├── seed_data.py         # Catálogo base (276 síntomas, 51 enfermedades, 51 tratamientos)
│   ├── seed_demo.py         # Datos demo idempotentes
│   ├── regenerate_reports.py
│   ├── requirements.txt
│   └── .env.example         # variables saneadas (sin credenciales reales)
├── frontend/
│   ├── src/chat/            # ClinicalShell, AiWorkspace, HistoryPhase, visor PDF
│   ├── src/pages/           # Login, panel admin, portal del paciente
│   ├── src/styles/          # mimetic.css (Tailwind aislado, preflight: false)
│   └── vite.config.ts       # proxy /api -> 127.0.0.1:8001
├── docker-compose.yml       # MongoDB local
├── DATOS_PRUEBA.md          # guion de prueba y alcance real/simulado
└── README_V1.2.md           # este documento
```

## Verificación realizada

- `npm run build` correcto.
- `npm run test` → 6/6 pruebas.
- `npm run lint` → 0 errores (7 warnings preexistentes).
- `python -m py_compile` del backend correcto.
- `/health` → `database: connected`.
- 7/7 reportes demo regenerados con el nuevo diseño.
- Ciclo completo verificado: búsqueda de paciente → atenciones → vista previa →
  impresión/PDF, incluido el estado "sin documento".

## Alcance y límites

Real: autenticación, búsqueda de pacientes, historias y sesiones en MongoDB, triaje y
laboratorio persistidos, motor experto local, documento HTML y consolidada.

Simulado o roadmap: bundle FHIR R4 (sin validación HL7 ni envío), ECG, solicitud de
camas, dictado por voz, MFA/WebAuthn/YubiKey, firma electrónica y envío a HIS.

La descarga del PDF depende del diálogo del navegador (**Guardar como PDF**); no se
incluye una librería de generación de PDF en el servidor.

## Seguridad

- Este paquete **no incluye** el `.env` real ni secretos de correo, IA u OAuth.
- Usa `backend/.env.example` como plantilla y define un `JWT_SECRET` propio.
- El archivo `.gitignore` ya excluye `.env`, `.venv/`, `node_modules/` y `dist/`.
