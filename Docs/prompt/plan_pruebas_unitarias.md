# Plan de Pruebas Unitarias — MIMETIC IA (V._1.2)

> **Proyecto:** `Mimetic_V._1.2` (backend FastAPI + frontend React/Vite)  
> **Rama:** `Manueldev`  
> **Fecha:** 2026-11-19  
> **Objetivo:** Alcanzar cobertura ≥ 80 % en lógica de negocio y ≥ 60 % global, con suites reproducibles en CI.

---

## 1. Objetivos

1. Garantizar la **seguridad clínica** del motor experto (diagnóstico, negación, dosis).
2. Evitar regresiones en normalización del catálogo (acentos, case, colisiones).
3. Validar autenticación/autorización (RBAC) y validación de entrada.
4. Proteger la generación de reportes HTML/PDF y la plantilla clínica.
5. Cubrir componentes críticos del frontend (chat, búsqueda, portal del paciente).

## 2. Stack de testing

### Backend (Python 3.11+)

| Herramienta | Uso |
|---|---|
| `pytest` | Runner principal |
| `pytest-asyncio` | Tests async (Motor/Mongo) |
| `pytest-cov` | Cobertura |
| `httpx` / `fastapi.testclient.TestClient` | Tests de rutas (síncronos) |
| `mongomock` / `mongomock-motor` | Mock de MongoDB para tests de integración |
| `freezegun` | Congelar fechas (seed_demo, JWT exp) |
| `pytest-mock` / `unittest.mock` | Mock de SMTP, Gmail API, LLM providers |
| `factory-boy` (opcional) | Fixtures de usuarios/historias |

### Frontend (Node 20+)

| Herramienta | Uso |
|---|---|
| `vitest` | Runner (ya configurado) |
| `@testing-library/react` | Render de componentes |
| `@testing-library/user-event` | Interacciones |
| `msw` | Mock de API (handlers) |
| `vitest --coverage` (v8) | Cobertura |

## 3. Configuración base

### Backend — `pytest.ini` (ampliar el existente)

```ini
[pytest]
asyncio_mode = auto
testpaths = tests
addopts = -ra --strict-markers --cov=app --cov-report=term-missing --cov-fail-under=70
markers =
    unit: pruebas puras sin I/O
    integration: requieren MongoDB (mongomock o real)
    slow: tests lentos (seed, reportes)
```

### Frontend — `vite.config.ts` (test)

Ya existe `npm run test`. Añadir:

```ts
test: {
  environment: 'jsdom',
  setupFiles: ['src/test/setup.ts'],
  coverage: { provider: 'v8', reporter: ['text', 'html'], thresholds: { lines: 60 } },
}
```

## 4. Pirámide de pruebas

```
        /\
       /E2E\        (Playwright, opcional, flujos críticos)
      /------\
     / Integr.\    (API + DB mongomock, auth, CRUD, reportes)
    /----------\
   /   Unit     \  (puras: normalizer, matcher, engine, utils, models, hooks)
  /--------------\
```

Prioridad: **Unit > Integration > E2E**.

## 5. Backend — Plan por módulo

### 5.1 `app/expert_system/normalizer.py` (ALTA prioridad)

Funciones clave: `_strip_accents`, `_fold`, `_norm`, `clean_text`, `clean_list`, `is_blank`, `find_symptom`, `find_negated_symptoms`, `extract_symptoms_from_vitals`, `_keyword_decompose`, `_build_specific_question`.

Casos:
- Normalización de acentos/case (`Vómito` → `vomito`).
- Colapso de duplicados por clave normalizada.
- Detección de síntomas negados (`"no tengo fiebre"` → excluido).
- Descomposición de keywords y coincidencia parcial.
- Síntomas extraídos de signos vitales (fiebre > 37.5, taquipnea, PA alta).
- Entradas vacías/blancas → `is_blank` True.

### 5.2 `app/expert_system/matcher.py`

Funciones: `calculate_match`, `_excluded_penalty`, `build_symptom_weights`.

Casos:
- Un solo síntoma genérico → score 0 / sin diagnóstico.
- Perfil completo → enfermedad correcta en primer lugar.
- Síntomas excluidos → penalización (hard penalty en cardinales).
- Pesos IDF: síntomas raros pesan más que comunes.
- Entradas con acentos → coincidencia.

### 5.3 `app/expert_system/engine.py`

Funciones: `narrow_diagnoses`, `_apply_demographic_adjustment`, `_demographic_profile`, `_symptom_gap`, `classify_conversation`, `is_greeting`, `is_goodbye`, `is_thank_you`, `is_report_request`, `is_conversational`, `generate_followup`.

Casos:
- Narrowing dinámico con múltiples candidatos.
- Ajuste demográfico por edad/sexo (secondary_score).
- Clasificación de intención (saludo, despedida, reporte, conversacional).
- Generación de pregunta discriminante.

### 5.4 `app/expert_system/conversation.py`

Funciones: `converse`, `generate_followup`, `diagnose_symptoms`.

Casos (con mock de DB):
- Flujo completo de conversación (síntomas → diagnóstico → tratamiento).
- Manejo de entrada vacía / síntomas no reconocidos.
- Persistencia de sesión (mock).

### 5.5 `app/data_treatment/` (cleaner, mapper, pipeline)

Funciones: `clean_text`, `clean_list`, `RowNormalizer`, `_infer_target`, `_parse_tabular_docs`, `_parse_json_docs`, `_alias_key`, `_clean_field_name`, `_match_disease_alias`, `_merge_unique`.

Casos:
- Limpieza de campos (HTML, espacios, acentos).
- Mapeo de alias (sinónimos).
- Pipeline idempotente (upsert por clave normalizada).
- Detección de colisiones (Vómito/vomito).

### 5.6 `app/auth/` (dependencies, permissions)

Funciones: `create_access_token`, `get_current_user`, `require_admin`, `require_super_admin`, `verify_social_token`.

Casos:
- Token válido → usuario extraído.
- Token expirado / inválido → 401.
- RBAC: medico no accede a rutas admin (403).
- Verificación de correo (código 6 dígitos, expiración 10 min).

### 5.7 `app/models/` (Pydantic)

Validación de esquemas: `UserCreate`, `ClinicalHistoryCreate`, `DiseaseCreate`, etc.

Casos:
- Campos requeridos faltantes → ValidationError.
- Tipos incorrectos → ValidationError.
- Valores límite (peso, edad, dosis).

### 5.8 `app/database/mongodb.py`

Funciones: `connect_db`, `close_db`, `get_db`, `db_is_ready`, `ensure_connected`, `create_indexes`.

Casos (con mongomock):
- Conexión exitosa → `db_is_ready` True.
- Reintento ante fallo (max_retries).
- Índices creados.

### 5.9 `app/reports/history_document.py`

Funciones: `build_report_model`, `_render_*`, `_e`, `_fmt_date`, `_fmt_time`, `_initials`, `_pct`, `_section`.

Casos:
- Renderizado de secciones (vitals, labs, triage, diagnósticos, prescripción).
- Escape HTML (XSS) en `_e`.
- Formato de fechas/horas.
- Reporte con datos vacíos → secciones vacías correctas.

### 5.10 `app/routes/` (integración)

Rutas: auth, diagnose, converse, clinical_history, report, knowledge, hospitals, patient, patient_portal.

Casos (TestClient + mongomock):
- `/health` → 200 + database connected.
- `/api/auth/register` → 201, correo verificado bloqueado hasta código.
- `/api/auth/login` → token válido; credenciales inválidas → 401.
- `/api/auth/verify-email` → código válido → activo; inválido/expirado → 400.
- `/api/diagnose` → lista de síntomas → diagnósticos.
- `/api/converse` → flujo conversacional.
- `/api/clinical-history` CRUD + búsqueda por documento.
- `/api/report` → HTML generado.
- `/api/knowledge/*` → RBAC (super_admin importa; medico solo lectura).
- Rate limiting (slowapi) → 429 tras exceso.

### 5.11 `app/config.py`, `logging_config.py`, `rate_limit.py`, `utils.py`

Casos:
- Carga de variables de entorno (defaults, obligatorias).
- Logging estructurado JSON.
- Rate limiter configurado.

### 5.12 `app/email/sender.py`

Funciones: `_send`, `_send_smtp`, `_send_gmail_api`, `_send_sendgrid`, `_is_local_url`, `_strip_insecure_params`, `_tls_enabled`, `_build_html`.

Casos (mock de red):
- Selección de proveedor (SMTP → Gmail API → SendGrid fallback).
- Escape de parámetros inseguros en URL.
- Construcción de HTML del correo.

## 6. Frontend — Plan por módulo

### 6.1 Hooks y contexto

- `useChatApp.ts` — estado del chat, fases, navegación, persistencia.
- `AuthContext.tsx` — login/logout, token, roles.

Casos:
- Transiciones de fase (search → patient → symptoms → report).
- Manejo de errores de API.
- Persistencia de sesión en localStorage.

### 6.2 API client

- `api/client.ts`, `api/patient.ts`, `api/errors.ts`.

Casos:
- Construcción de headers (Authorization).
- Manejo de errores HTTP (4xx/5xx) → `ApiError`.
- Retry / timeout.

### 6.3 Componentes críticos

- `SearchPhase.tsx` (ya tiene tests) — ampliar (búsqueda vacía, loading, selección).
- `SymptomsPhase.tsx` — selección de síntomas, dictado, vitales.
- `PatientInfoPhase.tsx` — validación de datos del paciente.
- `HistoryPhase.tsx` — búsqueda por documento, timeline.
- `ReportPhase.tsx` — vista previa, impresión/PDF.
- `ClinicalShell.tsx` — layout, navegación.
- `ProtectedRoute.tsx` — redirección por rol.
- `ErrorBoundary.tsx` — captura de errores.
- `SocialLogin.tsx` — flujo OAuth (mock).
- Admin: `CreateUserForm`, `UserList`, `ExpertSystemImport`.

Casos por componente:
- Render correcto con props mínimas.
- Interacciones (click, change, submit).
- Estados (loading, error, empty).
- Accesibilidad básica (roles, labels).

### 6.4 Utilidades y constantes

- `chat/constants.ts`, `chat/types.ts`, `chat/ui.tsx`.
- `data/locations.ts`.

Casos:
- Constantes no vacías.
- Tipos válidos (compilación TS).

### 6.5 Páginas

- `Login.tsx`, `Register.tsx`, `AdminPanel.tsx`, `PatientDashboard.tsx`.

Casos:
- Formulario de login: validación, submit, error.
- Registro: verificación de correo.
- Dashboard del paciente: carga de historias.

## 7. Mocks y fixtures

### Backend

- `conftest.py` con fixtures:
  - `mongo_db` (mongomock async).
  - `client` (TestClient con override de `get_db`).
  - `auth_token` (JWT de prueba para cada rol).
  - `seeded_catalog` (carga seed_data en mongomock).

Ejemplo:

```python
# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from mongomock_motor import AsyncMongoMockClient
from app.main import app
from app.database.mongodb import get_db

@pytest.fixture
def db():
    client = AsyncMongoMockClient()
    return client["mimetic_ai"]

@pytest.fixture
def client(db):
    app.dependency_overrides[get_db] = lambda: db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
```

### Frontend

- `msw` handlers en `src/test/handlers.ts` para `/api/*`.
- `setup.ts` con `@testing-library/jest-dom`.

## 8. Integración con DB (mongomock)

Tests que requieren DB se marcan `@pytest.mark.integration`. En CI se ejecutan con mongomock (sin servicio real). Tests que requieran Atlas real se marcan `@pytest.mark.atlas` y se saltan en CI por defecto.

## 9. CI/CD

### GitHub Actions (`.github/workflows/tests.yml`)

```yaml
name: Tests
on: [push, pull_request]
jobs:
  backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.11' }
      - run: pip install -r Mimetic_V._1.2/backend/requirements.txt -r Mimetic_V._1.2/backend/requirements-dev.txt
      - run: cd Mimetic_V._1.2/backend && pytest
  frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '20' }
      - run: cd Mimetic_V._1.2/frontend && npm ci && npm run test -- --coverage
```

Añadir `requirements-dev.txt` con: `pytest`, `pytest-asyncio`, `pytest-cov`, `mongomock-motor`, `freezegun`, `pytest-mock`.

## 10. Métricas y reporte

- Cobertura mínima: backend 70 % líneas, frontend 60 %.
- Reporte HTML en `htmlcov/` (gitignored).
- Tests fallidos bloquean merge (branch protection).

## 11. Cronograma por fases

| Fase | Semana | Entregable |
|---|---|---|
| F0 — Setup | 1 | conftest, MSW handlers, CI pipeline |
| F1 — Unit puros (normalizer, matcher, engine, utils, models) | 2-3 | ≥ 120 tests, cobertura 50 % |
| F2 — Integración (auth, routes, DB) | 4-5 | ≥ 80 tests, cobertura 70 % |
| F3 — Frontend (componentes, hooks) | 6-7 | ≥ 60 tests, cobertura 60 % |
| F4 — Reportes y email | 8 | ≥ 30 tests |
| F5 — E2E (Playwright, opcional) | 9 | 5 flujos críticos |

## 12. Riesgos y mitigaciones

| Riesgo | Mitigación |
|---|---|
| Tests lentos por seed (7000 líneas) | Cargar seed una vez por sesión (`scope="session"`), usar subconjuntos. |
| Dependencia de MongoDB real | mongomock-motor para unit/integration; Atlas solo en staging. |
| Mocks de email/IA frágiles | Interfaces abstractas (`EmailSender`, `AIProvider`) con implementaciones mockeables. |
| Flakiness por fechas | `freezegun` en tests que usen `datetime.utcnow()`. |
| Cobertura baja en UI compleja | Priorizar lógica extraída a hooks/utils; tests de componente solo para flujos críticos. |

## 13. Convenciones de nombres

- Backend: `tests/test_<modulo>.py`, funciones `test_<comportamiento>_<condicion>`.
- Frontend: `*.test.tsx` junto al componente.
- Markers: `@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.slow`.

## 14. Próximos pasos inmediatos

1. Crear `tests/conftest.py` con fixtures mongomock + client + tokens.
2. Implementar tests de `normalizer` y `matcher` (ya existe base en `test_matcher.py`, `test_normalization.py`).
3. Añadir tests de `engine` (narrowing, clasificación).
4. Configurar MSW en frontend y ampliar `SearchPhase.test.tsx`.
5. Activar CI en GitHub Actions.

---

**Fin del plan.** Este documento es la hoja de ruta; la implementación se hace por fases según el cronograma.
