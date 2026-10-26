# MIMETIC Backend

API en **Python 3.11+ / FastAPI** con **Motor (MongoDB async)**. Sistema experto médico (diagnóstico + tratamiento) con normalización estricta del catálogo, CRUD de conocimiento, importación de archivos CSV/Excel/JSON (solo `super_admin`) y verificación de correo.

## Puesta en marcha

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --port 8001 --reload
# Swagger UI: http://localhost:8001/docs
```

## Variables de entorno

Todas son opcionales salvo la conexión a MongoDB. Ver `app/config.py` (prefijos exactos):

| Variable | Uso |
|----------|-----|
| `MONGODB_URL` | Cadena de conexión a MongoDB Atlas |
| `MONGODB_DB_NAME` | Nombre de la base de datos (default `mimetic_ai`) |
| `JWT_SECRET` | Clave de firma de tokens |
| `JWT_ALGORITHM` | Algoritmo JWT (default `HS256`) |
| `JWT_EXPIRATION_HOURS` | Expiración del token en horas (default 24) |
| `FROM_EMAIL` | Remitente de correos |
| `SMTP_HOST` / `SMTP_PORT` / `SMTP_USE_SSL` / `SMTP_USER` / `SMTP_PASSWORD` | SMTP (fallback) |
| `GMAIL_API_CLIENT_ID` / `GMAIL_API_CLIENT_SECRET` / `GMAIL_API_REFRESH_TOKEN` | Gmail API (HTTPS) |
| `SENDGRID_API_KEY` | SendGrid (fallback de correo) |
| `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` | OAuth de Google |
| `OPENAI_API_KEY` / `OPENAI_BASE_URL` / `OPENAI_MODEL` | Proveedor OpenAI (alternativa a Gemini) |
| `GEMINI_API_KEY` / `GEMINI_MODEL` | Gemini (motor de lenguaje del diagnóstico) |
| `TOGETHER_API_KEY` | Together (alternativa) |
| `CORS_ORIGINS` | Orígenes permitidos (separados por coma) |
| `LOG_LEVEL` | Nivel de logging (JSON estructurado con request_id) |

> En Render usa `MONGODB_URL` y demás; en desarrollo local se cargan desde `.env` (comportamiento: `GMAIL_API_*` para envío real por HTTPS, `SMTP_*` como fallback).

## Módulos principales

```
backend/
├── main.py                  # App FastAPI, CORS, rate limit, logger, auto-seed, /health
├── seed_data.py             # Catálogo base: 276 síntomas, 51 enfermedades, 51 tratamientos
├── import_from_excel.py     # Importación desde archivos (Excel/CSV/JSON)
├── app/
│   ├── config.py            # Variables de entorno
│   ├── database/mongodb.py  # Conexión Motor async, reconnect, ping real
│   ├── auth/                # JWT, permisos (super_admin/admin/medico/paciente), RBAC
│   ├── auth/oauth.py        # Google OAuth
│   ├── roles.py             # require_roles / require_min_role (RBAC estricto)
│   ├── data_treatment/      # Limpieza y entrenamiento del catálogo (motor de datos)
│   ├── expert_system/       # Motor de diagnóstico (matcher, matching, conversación)
│   ├── models/              # Pydantic models (User, ClinicalHistory, Disease, Symptom, ...)
│   ├── routes/
│   │   ├── auth.py          # register, login, verify-email, create-user, me, ...
│   │   ├── diagnosis.py     # /api/converse (chat) y /api/diagnose
│   │   ├── knowledge.py     # CRUD symptoms/diseases/treatments + /import-file (super_admin)
│   │   ├── clinical_history.py / report.py / patient.py / converse.py / hospitals.py
│   └── utils.py             # normalize_text() — normalización estricta (sin diacríticos + lowercase)
```

## Normalización estricta del catálogo

Toda clave de conocimiento (`name` de síntomas/enfermedades/tratamientos) se normaliza a **minúsculas sin diacríticos** al insertar, importar y durante el seed (upsert idempotente por clave normalizada). Esto **colapsa colisiones** tipo `Vómito/vomito` y evita duplicados por acentos. Se aplica en:

- `app/utils.py` → `normalize_text()` (función central)
- `seed_data.py` → `dedupe_collection` / `_upsert_many`
- `import_from_excel.py` → `_split_symptoms` y validación del catálogo
- `routes/knowledge.py` → CRUD normalizado y `import_file`

El motor de matching usa la misma normalización (ver `expert_system/matcher.py`), por lo que el catálogo y el diagnóstico siempre comparan claves equivalentes.

## Endpoints

### Autenticación y usuarios
| Método | Ruta | Rol | Descripción |
|--------|------|-----|-------------|
| POST | `/api/auth/register` | público | Registro con verificación de correo (6 dígitos, 10 min) |
| POST | `/api/auth/login` | público | Inicio de sesión |
| POST | `/api/auth/verify-email` | público | Confirmar código de verificación |
| POST | `/api/auth/social-login` / `social-register` | público | Google OAuth |
| POST | `/api/auth/create-user` | admin/super_admin | Crear usuario |
| GET | `/api/auth/me` | autenticado | Perfil actual |
| GET | `/api/auth/users` | admin/super_admin | Listar usuarios |

### Diagnóstico
| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/api/converse` | Chat conversacional de diagnóstico (el sistema pregunta para discriminar) |
| POST | `/api/diagnose` | Diagnosticar a partir de una lista de síntomas |
| POST | `/api/report` | Generar historia clínica en PDF |

### Conocimiento (sistema experto)
| Método | Ruta | Rol | Descripción |
|--------|------|-----|-------------|
| GET | `/api/knowledge/symptoms` | autenticado | Síntomas registrados |
| GET | `/api/knowledge/diseases` | autenticado | Enfermedades registradas |
| GET | `/api/knowledge/treatments` | autenticado | Tratamientos registrados |
| POST | `/api/knowledge/import-file` | **super_admin** | Subir CSV/Excel/JSON con síntomas, enfermedades o tratamientos (multipart `file` + `collection`) |
| POST | `/api/knowledge/{collection}/bulk` | super_admin | Inserción masiva (JSON) |
| GET/POST/PUT/DELETE | `/api/knowledge/{collection}/{id}` | según rol | CRUD normalizado |

> `POST /api/knowledge/import-file` acepta `Content-Type: multipart/form-data` con campos `file` (archivo) y `collection` (`symptoms` | `diseases` | `treatments`). Realiza upsert idempotente y responde `{ inserted, updated, errors }`. Solo `super_admin` (los `admin` reciben 403).

### Estado
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/health` | Health check con ping real a MongoDB |

## Tests

```bash
cd backend
pytest -q
```

Cubren normalización, seed idempotente, dedupe, CRUD del catálogo, importación multipart, RBAC y endpoints de conocimiento.
