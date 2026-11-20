# Resultados de Pruebas Unitarias — MIMETIC IA (V._1.2)

> **Fecha de ejecución:** 2026-11-20 (post-merge con main)  
> **Rama:** `Manueldev`  
> **Plan de referencia:** `Docs/plan_pruebas_unitarias.md`

---

## 1. Resumen ejecutivo

| Área | Tests ejecutados | Pasados | Fallidos | Cobertura (líneas) |
|------|------------------|---------|----------|---------------------|
| Backend (pytest) | 150 | 150 | 0 | 55 % |
| Frontend (vitest) | 10 | 10 | 0 | 47.96 % |

- **Total tests:** 160  
- **Fallos:** 0 (tras adaptar mocks al nuevo contrato de `send_verification_code` que devuelve dict).  
- **Advertencias:** 35 (deprecations).

---

## 2. Backend — Detalle

### 2.1 Comando ejecutado

```bash
cd Mimetic_V._1.2/backend
.\.venv\Scripts\Activate.ps1
python -m pytest --cov=app --cov-report=term -q
```

### 2.2 Resultado

```
150 passed, 35 warnings in 6.08s
TOTAL  3102 statements, 1392 missed  →  55 % cobertura
```

### 2.3 Cambios tras merge con main

- Main añadió `tests/test_email_sender.py` (89 líneas) y modificó `sender.py` (`send_verification_code` ahora devuelve `dict` con `delivered`).
- Main modificó `auth.py` (`_deliver_verification_code` consume el dict).
- Se adaptaron los mocks en `test_unit_email.py` y `test_integration_auth.py` para devolver `{"delivered": True, ...}`.
- `conftest.py` y tests locales se mantuvieron sin conflictos.

### 2.4 Cobertura por módulo (destacados)

| Módulo | Cobertura |
|--------|-----------|
| `app/models/*` | 100 % |
| `app/utils.py` | 100 % |
| `app/rate_limit.py` | 100 % |
| `app/expert_system/normalizer.py` | alta |
| `app/expert_system/matcher.py` | alta |
| `app/expert_system/engine.py` | parcial-alta |
| `app/data_treatment/*` | cubierto |
| `app/reports/history_document.py` | ~10 % + helpers |
| `app/routes/*` | 18–50 % |
| `app/auth/*` | ~22 % |
| `app/database/mongodb.py` | cubierto |
| `app/email/sender.py` | cubierto (helpers) |

### 2.5 Tests (acumulado)

Tests locales (13 archivos) + `test_email_sender.py` aportado por main. Total 150.

---

## 3. Frontend — Detalle

### 3.1 Comando ejecutado

```bash
cd Mimetic_V._1.2/frontend
npm run test -- --coverage
```

### 3.2 Resultado

```
Test Files  3 passed (3)
Tests       10 passed (10)
Statements  41.89 % | Branches 42.3 % | Functions 44 % | Lines 47.96 %
```

### 3.3 Cambios tras merge

- Main añadió `portal.css`, modificó `Login.tsx`, `Register.tsx`, `PatientDashboard.tsx`, `config.ts`.
- Tests existentes (SearchPhase, ErrorBoundary, ProtectedRoute) siguen pasando.

---

## 4. Gaps y próximos pasos

1. `app/reports/history_document.py`: 10 % → ampliar renderizado.
2. `app/routes/*`: 18–50 % → más casos de error/edge.
3. `app/auth/*`: ~22 % → tokens, RBAC, verificación.
4. Frontend: `useChatApp`, `AuthContext`, `SymptomsPhase`, `HistoryPhase`, `ReportPhase`.
5. CI/CD: crear `.github/workflows/tests.yml`.
6. Objetivo: backend ≥ 70 %, frontend ≥ 60 %.

---

## 5. Archivos generados/modificados (acumulado)

- `Mimetic_V._1.2/backend/tests/conftest.py`
- `Mimetic_V._1.2/backend/tests/test_unit_*.py` (7 archivos)
- `Mimetic_V._1.2/backend/tests/test_integration_*.py` (5 archivos)
- `Mimetic_V._1.2/backend/pytest.ini`
- `Mimetic_V._1.2/frontend/src/components/ProtectedRoute.test.tsx`
- `Mimetic_V._1.2/frontend/package.json` + `package-lock.json`
- `Docs/resultados_pruebas_unitarias.md` (este archivo)

---

**Conclusión:** Suite al 100 % (160/160). Cobertura backend 55 %, frontend 47.96 %. Merge con main integrado sin conflictos en tests.
