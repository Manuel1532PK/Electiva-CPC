# MIMETIC IA — Gemelos Digitales

> **Versión 1.2** — incluye el rediseño de login, espacio de IA, historial clínico y
> documentos PDF. Consulta [`README_V1.2.md`](./README_V1.2.md) para el alcance, la
> estructura y el arranque local de este paquete.

Sistema conversacional de apoyo al diagnóstico médico. El médico registra al paciente, describe los síntomas en lenguaje natural y el sistema devuelve diagnósticos diferenciales con tratamientos, ajusta dosis por peso/edad/embarazo/alergias y genera la historia clínica en PDF.

> Desarrollado bajo una arquitectura de **conocimiento en MongoDB Atlas** (catálogo de enfermedades, síntomas y tratamientos alimentado mediante seed idempotente, CRUD normalizado e importación de archivos CSV/Excel/JSON desde la UI de `super_admin`).

## Stack

| Capa | Tecnología |
|------|-----------|
| Backend | Python 3.11+ / FastAPI (Motor MongoDB async) |
| Frontend | React + Vite + TypeScript |
| Base de datos | MongoDB Atlas (Motor async, TLS real) |
| Correo | SMTP Gmail + Gmail API (HTTPS) + SendGrid |
| IA | Gmail API / Gemini / OpenAI / Together (AI Provider interchangeable) |
| Autenticación | JWT + Google OAuth (correo verificado por código de 6 dígitos) |

## Arquitectura

```
┌─────────────┐     ┌──────────────┐     ┌───────────┐
│  Frontend   │────▶│   Backend    │────▶│ MongoDB   │
│ React/Vite  │     │  FastAPI     │     │ Atlas     │
│ Vercel      │◀────│  Render      │     │           │
└─────────────┘     └──────────────┘     └───────────┘
                        │  Gmail API / Gemini / OpenAI / Together
                        ▼
                  Correos y LLM
```

## Roles (RBAC)

| Rol | Acceso |
|-----|--------|
| `super_admin` | Todo: panel, CRUD completo e **importación de archivos** de conocimiento, gestión de usuarios/hospitales |
| `admin` | Panel de administración, crear usuarios, gestionar hospitales |
| `medico` | Chat de diagnóstico, historias clínicas, aprobar/descartar tratamientos |
| `paciente` | Consulta sus diagnósticos y tratamientos |

> **Verificación de correo:** todo registro (correo o Google) queda bloqueado hasta confirmar un código de 6 dígitos (válido 10 min). Incluye registro social con Google (OAuth + verificación de correo).

## Fases implementadas

### FASE 1 — Control del doctor sobre diagnóstico y tratamiento
- `medico` aprueba, modifica o descarta los fármacos sugeridos (dosis/contraindicaciones) antes de validar el plan.
- Ajuste de dosis pediátrico por peso (mg/kg) y selección de medicamentos bajo guías colombianas.
- Filtro por alergias, embarazo y comorbilidades.

### FASE 2 — Exactitud del diagnóstico
- Ponderación IDF y `secondary_score` por demografía (edad/sexo) para ordenar los diferenciales.
- Motor de **data_treatment**: limpieza y entrenamiento del catálogo (mapping de sinónimos, colisiones).
- Preguntas discriminantes cuando hay varios diagnósticos posibles (narrowing dinámico).
- Auto-detección de síntomas desde signos vitales (fiebre > 37.5, taquipnea, PA alta, etc.).
- Explicaciones en español sencillo para el paciente (`patient_summary`).

### Normalización estricta (colisiones tipo Vomito/vomito)
- Claves del catálogo (`name`, `disease_name`) normalizadas a **minúsculas y sin diacríticos** en seed, importación y CRUD.
- Colapsa duplicados por acento/case (`Vómito/vomito`, `Cefalea/cefalea`) de forma idempotente (upsert por clave normalizada, conserva el menor `_id`).

### Sistema experto — alimentación de la base de conocimiento
- Interfaz **super_admin** "Sistema experto" en el panel para importar `symptoms`, `diseases` y `treatments` desde archivos **CSV, Excel (XLSX) o JSON**.
- Endpoint `POST /api/knowledge/import-file` (multipart) que valida la colección (`symptoms|diseases|treatments`), normaliza y hace **upsert idempotente** contra Atlas.
- CRUD completo del catálogo con límites de rol.

## Catálogo actual (seed)

| Colección | Registros | Claves |
|-----------|----------|--------|
| `symptoms` | 276 | `name`, `description`, `category` |
| `diseases` | 51 | `name`, `description`, `symptoms`, `severity` |
| `treatments` | 51 | `disease_name`, `medicines`, `alternative_medicines`, `non_pharmacological_treatments` |

Además: `users`, `hospitals`, `clinical_histories`, `sessions` (ver `FASE 1`).

## Inicio rápido

```bash
# Backend (puerto 8001)
cd backend
pip install -r requirements.txt
uvicorn main:app --port 8001 --reload

# Frontend (puerto 5173)
cd frontend
npm install
npx vite --port 5173
```

Variables de entorno (backend, ver `config.py` y `.env.example`):
- `MONGODB_URL` — MongoDB Atlas
- `MONGODB_DB_NAME` — base de datos
- `JWT_SECRET` / `JWT_ALGORITHM` / `JWT_EXPIRATION_HOURS` — token
- `SMTP_*` — credenciales Gmail SMTP
- `GMAIL_API_CLIENT_ID` / `GMAIL_API_CLIENT_SECRET` / `GMAIL_API_REFRESH_TOKEN` — Gmail API (HTTPS)
- `SENDGRID_API_KEY` — SendGrid (fallback)
- `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` — Google OAuth (login)
- `OPENAI_API_KEY` / `OPENAI_BASE_URL` / `OPENAI_MODEL` — provider de IA
- `GEMINI_API_KEY` / `GEMINI_MODEL` — Gemini
- `TOGETHER_API_KEY` — Together
- `CORS_ORIGINS` — orígenes permitidos (separados por comas)
- `LOG_LEVEL` — nivel de logging (JSON estructurado)

## API

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/api/auth/register` | Registro de paciente (verifica correo) |
| POST | `/api/auth/login` | Inicio de sesión |
| POST | `/api/auth/verify-email` | Confirmar código de 6 dígitos |
| POST | `/api/auth/social-login` * status | Inicio de sesión con Google |
| POST | `/api/auth/social-register` | Registro con Google |
| POST | `/api/auth/create-user` | Crear usuario (admin/super_admin) |
| GET | `/api/auth/me` | Perfil del usuario autenticado |
| GET | `/api/auth/users` | Listar usuarios (admin) |
| POST | `/api/converse` | Chat conversacional de diagnóstico |
| POST | `/api/diagnose` | Diagnosticar por lista de síntomas |
| POST | `/api/report` | Generar historia clínica en PDF |
| POST | `/api/clinical-history` | Crear historia clínica |
| GET | `/api/clinical-history/search` | Buscar paciente por documento |
| GET | `/api/knowledge/symptoms` | Síntomas registrados |
| GET | `/api/knowledge/diseases` | Enfermedades registradas |
| GET | `/api/knowledge/treatments` | Tratamientos registrados |
| POST | `/api/knowledge/import-file` | Importar CSV/Excel/JSON (super_admin) |
| GET | `/health` | Estado del servicio |

> *Listado completo con métodos/roles en el `README` de `backend`.*

## Despliegue

- **Frontend**: Vercel — configurar `REACT_APP_API_URL` / `VITE_API_URL` apuntando al backend.
- **Backend**: Render (Web Service) — con `start_backend.ps1`.
- **Base de datos**: MongoDB Atlas.

## Documentación

- [Backend](./backend/README.md) — arquitectura, endpoints, módulos (sistema experto, data_treatment, seguridad).
- [Frontend](./frontend/README.md) — estructura, páginas, componentes admin (sistema experto).
```
