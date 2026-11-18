# Plan de auditoría técnica — MIMETIC AI v1.2

**Proyecto:** MIMETIC AI — sistema conversacional de apoyo al diagnóstico médico (Electiva CPC / Semillero Quantum, UNIMINUTO)
**Objeto auditado:** carpeta `Mimetic_V._1.2/`
**Tipo de entrega:** plan de auditoría (no ejecución)
**Fecha:** 18 de noviembre de 2026
**Modo de trabajo:** solo lectura. No se modificó, movió ni borró ningún archivo del proyecto. Este documento se generó fuera de `Mimetic_V._1.2/`.

---

## Convenciones de evidencia

| Etiqueta         | Significado                                                                                     |
| ---------------- | ----------------------------------------------------------------------------------------------- |
| **[HECHO]**      | Verificado directamente leyendo el archivo citado en esta sesión.                               |
| **[INDICIO]**    | Patrón de riesgo observado; requiere confirmación ejecutando el sistema o revisando más código. |
| **[SUPOSICIÓN]** | Inferencia razonable no verificada; se declara como tal.                                        |

**Alcance incluido:** todo el contenido de `Mimetic_V._1.2/` (`backend/`, `frontend/`, configuración y documentación de la raíz).
**Excluido:** `frontend/node_modules/`, `frontend/dist/`, `backend/__pycache__/`, `backend/**/__pycache__/`, `backend/.pytest_cache/`, `.env`, `.venv/`, `venv/`, `*.pyc`, `.DS_Store`, `Thumbs.db`, `.git/`.
**Sí se revisan** los archivos de ejemplo y configuración de despliegue: `.env.example`, `docker-compose.yml`, `render.yaml`, `vercel.json`, `vite.config.ts`, `pytest.ini`.

---

## Áreas solicitadas: aplicabilidad

Las 10 áreas aplican al proyecto. Única excepción parcial, declarada para no forzar un criterio inexistente:

| Área                              | Aplica          | Nota                                                                                                                                                                                                                                                                                                                                    |
| --------------------------------- | --------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1. Estructura y organización      | Sí              | Incluye revisar los directorios de la raíz del repo, no solo `Mimetic_V._1.2/`.                                                                                                                                                                                                                                                         |
| 2. Calidad del código             | Sí              | —                                                                                                                                                                                                                                                                                                                                       |
| 3. Seguridad                      | Sí              | Área prioritaria.                                                                                                                                                                                                                                                                                                                       |
| 4. Dependencias                   | Sí              | 15 deps backend + 24 deps frontend.                                                                                                                                                                                                                                                                                                     |
| 5. Configuración y ejecución      | Sí              | —                                                                                                                                                                                                                                                                                                                                       |
| 6. Pruebas                        | Sí              | —                                                                                                                                                                                                                                                                                                                                       |
| 7. Rendimiento                    | Sí              | —                                                                                                                                                                                                                                                                                                                                       |
| 8. Documentación                  | Sí              | —                                                                                                                                                                                                                                                                                                                                       |
| 9. Mantenibilidad y escalabilidad | Sí              | —                                                                                                                                                                                                                                                                                                                                       |
| 10. Licencias y cumplimiento      | Sí, **parcial** | **No aplica** el subcriterio "licencias de _recursos incluidos_": no se encontraron imágenes, fuentes, íconos ni datasets de terceros. El único binario es `frontend/public/logo.png` (marca propia) y los diagramas de `Docs/` son del equipo. Sí aplican las licencias de dependencias y el cumplimiento normativo en datos de salud. |

---

## 1. Resumen del proyecto

MIMETIC AI es un MVP avanzado (v1.2) de apoyo al diagnóstico: el médico registra paciente, anamnesis, antecedentes, signos vitales y laboratorio, describe síntomas en lenguaje natural y recibe diagnósticos diferenciales con tratamiento y ajuste de dosis; al cerrar la atención se genera una historia clínica imprimible y el paciente consulta su información en un portal propio.
Está organizado en dos aplicaciones: `backend/` (FastAPI + Motor/MongoDB, motor heurístico propio, sin LLM en runtime) y `frontend/` (React 18 + TypeScript + Vite, SPA con React Router).
El dominio clínico vive en `backend/app/expert_system/` y `backend/app/data_treatment/`; la autenticación en `backend/app/routes/auth.py` y `backend/app/auth/`; el catálogo se siembra desde `backend/seed_data.py`.
Es un prototipo académico, no un producto en producción: hay módulos simulados (FHIR R4, ECG, dictado por voz, MFA, solicitud de cama, firma electrónica) declarados en `README_V1.2.md`.

---

## 2. Inventario inicial de `Mimetic_V._1.2/`

### 2.1 Volumen y composición [HECHO]

| Métrica                     | Valor                                                                                                                                                                                                     |
| --------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Archivos (sin exclusiones)  | **124**                                                                                                                                                                                                   |
| Tamaño del código fuente    | **1,56 MB**                                                                                                                                                                                               |
| Extensiones                 | `.py` 57 · `.tsx` 26 · `.ts` 11 · `.json` 6 · `.md` 5 · `.txt` 3 · `.css` 3 · `.js` 2 · `.example` 2 · `.gitignore` 2 · resto (`.yaml`, `.yml`, `.png`, `.html`, `.ini`, `.cjs`, `.python-version`) 1 c/u |
| Endpoints HTTP              | **48** declarados en `backend/app/routes/`                                                                                                                                                                |
| Archivos de prueba backend  | 6 (`backend/tests/`)                                                                                                                                                                                      |
| Archivos de prueba frontend | 2 (`frontend/src/chat/SearchPhase.test.tsx`, `frontend/src/components/ErrorBoundary.test.tsx`)                                                                                                            |

> El peso real del árbol de trabajo es ~184 MB, pero ~173 MB son `frontend/node_modules/` y ~8,8 MB `frontend/dist/`, ambos generados y fuera del alcance.

### 2.2 Árbol resumido [HECHO]

```
Mimetic_V._1.2/
├── README.md                  visión general (incluye fase de análisis)
├── README_V1.2.md             alcance real vs. simulado (documento clave)
├── DATOS_PRUEBA.md            credenciales demo y sesiones sembradas
├── docker-compose.yml         MongoDB 7 local
├── .gitignore
├── backend/
│   ├── main.py                entrada FastAPI (CORS, rate limit, routers)
│   ├── .env.example / .python-version / runtime.txt / pytest.ini
│   ├── requirements.txt / requirements-dev.txt
│   ├── render.yaml            despliegue Render
│   ├── seed_data.py (6.986 líneas) / seed_demo.py (735)
│   ├── ai_generate_knowledge.py   script offline (Gemini/OpenAI)
│   ├── import_from_excel.py / migrate_data.py / regenerate_reports.py
│   ├── manage.py / manage_admin.py / setup_gmail_api.py
│   ├── app/
│   │   ├── auth/ (3)          JWT, dependencias, permisos
│   │   ├── database/ (2)      cliente Motor, índices, reconexión
│   │   ├── data_treatment/ (4) pipeline/mapper/cleaner de tratamientos
│   │   ├── email/ (2)         Gmail API / SMTP / SendGrid
│   │   ├── expert_system/ (5) engine, normalizer (1.196), conversation
│   │   ├── models/ (7)        Pydantic (user, patient, clinical_history…)
│   │   ├── reports/ (2)       history_document (1.322), generación
│   │   ├── routes/ (10)       auth, converse, diagnosis, knowledge,
│   │   │                      patient, patient_portal, report,
│   │   │                      clinical_history, hospitals
│   │   ├── rate_limit.py / logging_config.py / config.py
│   └── tests/ (6)
└── frontend/
    ├── index.html / vite.config.ts / vercel.json
    ├── package.json / package-lock.json / tsconfig*.json
    ├── eslint.config.js / tailwind.config.js / postcss.config.cjs
    ├── .env.example
    ├── public/logo.png
    └── src/
        ├── api/ (3)           client.ts (token), endpoints
        ├── chat/ (14)         fases del flujo conversacional + 1 test
        ├── components/ (7)    incluye ErrorBoundary + 1 test
        ├── context/ (1)       AuthContext.tsx
        ├── pages/ (4)         Login, Register, dashboards
        ├── data/ (1)          constants.ts
        ├── styles/ (1)
        └── test/ (1)          setup de Vitest
```

### 2.3 Puntos de entrada [HECHO]

| Tipo                   | Ruta                                                                                                                                                       | Observación                                                                    |
| ---------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------ |
| API (runtime)          | `backend/main.py`                                                                                                                                          | Monta 9 routers bajo `/api`; `app.state.limiter`; CORS; middleware de logging. |
| Scripts operativos     | `backend/manage.py`, `backend/manage_admin.py`, `backend/seed_data.py`, `backend/seed_demo.py`, `backend/migrate_data.py`, `backend/regenerate_reports.py` | Ejecutables manuales, sin empaquetado ni CLI unificada.                        |
| Script offline con LLM | `backend/ai_generate_knowledge.py`                                                                                                                         | Único lugar donde se usan Gemini/OpenAI/Together.                              |
| SPA                    | `frontend/index.html` → `frontend/src/`                                                                                                                    | Build Vite; `dist/` excluido.                                                  |
| Pruebas                | `backend/pytest.ini` (`testpaths = tests`)                                                                                                                 | `asyncio_mode = auto`.                                                         |

### 2.4 Archivos de configuración clave [HECHO]

| Archivo                   | Qué define                                   | Relevancia para la auditoría                                          |
| ------------------------- | -------------------------------------------- | --------------------------------------------------------------------- |
| `backend/app/config.py`   | Variables de entorno con valores por defecto | Línea 8: `JWT_SECRET` tiene default. Líneas 30-33: CORS por variable. |
| `backend/.env.example`    | Plantilla de 25+ variables                   | Comentarios correctos; valores sensibles vacíos.                      |
| `frontend/.env.example`   | `VITE_API_URL` opcional                      | Sin secretos.                                                         |
| `docker-compose.yml`      | MongoDB 7 en `27017:27017`                   | Sin usuario/contraseña de Mongo.                                      |
| `backend/render.yaml`     | Servicio Render                              | `repo:` apunta a otro repositorio.                                    |
| `frontend/vercel.json`    | Build y rewrites SPA                         | Sin cabeceras de seguridad.                                           |
| `frontend/vite.config.ts` | Proxy `/api` y `/health` a `127.0.0.1:8001`  | Puertos fijos.                                                        |
| `backend/pytest.ini`      | Config de pytest                             | Sin cobertura configurada.                                            |

---

## 3. Plan de auditoría

| Fase    | Área                                                | Qué se revisará                                                                                                                                                                                                                                                                                                   | Archivos/módulos                                                                                                                                                                                                                                                 | Método/herramienta                                                                                                                                                                                                                         | Prioridad | Esfuerzo                     |
| ------- | --------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------- | ---------------------------- |
| **F0**  | Estructura y organización                           | Higiene del árbol: archivos huérfanos, duplicados de documentación, residuos de build, `.gitignore`, nombres problemáticos (`Mimetic_V._1.2` con puntos), convivencia con el esqueleto de la raíz del repo                                                                                                        | `Mimetic_V._1.2/` completo; raíz del repo (`core/`, `agents/`, `skills/`, `tools/`, `interfaces/`, `config/`, `evaluations/`)                                                                                                                                    | `git ls-files`, `tree`/`Get-ChildItem`, búsqueda de imports cruzados (`grep -R "Mimetic" core/ agents/`), revisión manual                                                                                                                  | Baja      | 2–3 h                        |
| **F1**  | Seguridad — autenticación y sesión                  | Flujo registro → código de 6 dígitos → verificación: generación (PRNG), expiración, reintentos, almacenamiento, enumeración de usuarios, fuerza bruta; hashing bcrypt y costo; política de contraseña; JWT (algoritmo, expiración, revocación, refresh); almacenamiento del token y riesgo XSS                    | `backend/app/routes/auth.py`, `backend/app/auth/dependencies.py`, `backend/app/models/user.py`, `backend/app/config.py`, `frontend/src/api/client.ts`, `frontend/src/context/AuthContext.tsx`, `frontend/src/pages/Login.tsx`, `frontend/src/pages/Register.tsx` | Revisión manual + `bandit -r backend/app` + `semgrep --config p/owasp-top-ten` + pruebas con `httpx`/`curl` contra instancia local (fuerza bruta, reutilización de código, usuario enumerable) + `pip-audit` sobre `python-jose`/`passlib` | **Alta**  | 8–12 h                       |
| **F2**  | Seguridad — Google OAuth                            | Validación real del token en backend (`id_token` vs `access_token`, verificación de `aud`/`iss`/`exp`), vinculación de cuentas, confianza en email/nombre enviados por el cliente, rol por defecto asignado                                                                                                       | `backend/app/routes/auth.py` (`verify_social_token`, `social_login`, `social_register`), `frontend/src/components/SocialLogin.tsx`, `@react-oauth/google` en `frontend/package.json`                                                                             | Revisión manual + prueba de suplantación con token propio y email ajeno + replay de token expirado + `semgrep`                                                                                                                             | **Alta**  | 4–6 h                        |
| **F3**  | Seguridad — RBAC, BOLA/IDOR, escalada               | Que cada endpoint valide rol **y** propiedad del recurso; acceso cruzado entre pacientes, entre médicos, entre hospitales; posibilidad de auto-asignarse rol o crear `admin`/`super_admin`; separación de funciones de los 4 roles                                                                                | `backend/app/routes/patient.py`, `patient_portal.py`, `clinical_history.py`, `hospitals.py`, `knowledge.py`, `report.py`, `auth.py`, `backend/app/auth/permissions.py`                                                                                           | Revisión manual endpoint por endpoint (48 rutas) + matriz rol×recurso + pruebas automatizadas con dos usuarios de prueba (`pytest` + `httpx.AsyncClient`) + `semgrep` reglas de autorización                                               | **Alta**  | 8–10 h                       |
| **F4**  | Seguridad — inyección NoSQL y validación de entrada | Operadores `$` aceptados desde entrada del usuario, `$regex` sin escapar, límites de longitud, `data: dict` sin esquema, campos Pydantic sin restricción, `extra` permitido, tipos laxos (`str` en lugar de `EmailStr`), mass assignment                                                                          | `backend/app/routes/clinical_history.py` (líneas 83-125), `backend/app/routes/*.py`, `backend/app/models/*.py`                                                                                                                                                   | Revisión manual + `semgrep` (nosql-injection) + payloads de prueba (`{"$ne": null}`, `{"$regex": ".*"}`) + `bandit` + fuzzing básico con `schemathesis` (opcional)                                                                         | **Alta**  | 6–8 h                        |
| **F5**  | Dominio — motor de diagnóstico y dosificación       | Lógica heurística (IDF, cobertura, especificidad): empates, entradas vacías, ruido en lenguaje natural, casos borde; dosis por peso/edad con unidades, redondeos, máximos, contraindicaciones, alergias, embarazo, comorbilidades, valores nulos; trazabilidad de la sugerencia; avisos de "herramienta de apoyo" | `backend/app/expert_system/engine.py` (465), `normalizer.py` (1.196), `conversation.py`, `backend/app/data_treatment/{pipeline,mapper,cleaner}.py`                                                                                                               | Revisión manual + pruebas de caracterización (tabla de casos con entradas y salidas esperadas) + `pytest --cov` sobre el módulo + **revisión por profesional de salud** (obligatoria)                                                      | **Alta**  | 10–15 h + validación clínica |
| **F6**  | Dominio — historia clínica y reporte HTML           | XSS/inyección de HTML con datos del paciente, escapado, control de acceso al documento generado, descarga/impresión, integridad del contenido                                                                                                                                                                     | `backend/app/reports/history_document.py` (1.322), `backend/app/routes/report.py`, `frontend/src/chat/HistoryPhase.tsx`                                                                                                                                          | Revisión manual + payloads XSS en nombre/anamnesis + render en navegador + `bandit` + verificación de autorización del endpoint                                                                                                            | **Alta**  | 4–6 h                        |
| **F7**  | Seguridad — importación de catálogo                 | Tipo y tamaño de archivo, macros, fórmulas, validación de esquema y contenido, límites, quién puede importar, escritura masiva en Mongo, `pandas.read_excel` sobre archivos hostiles                                                                                                                              | `backend/app/routes/knowledge.py` (`/import-file`), `backend/import_from_excel.py`, `backend/app/data_treatment/pipeline.py`, `openpyxl`/`pandas` en `requirements.txt`                                                                                          | Revisión manual + carga de XLSX/CSV malformados y sobredimensionados + revisión de permisos (`super_admin`) + `pip-audit`                                                                                                                  | Media     | 3–4 h                        |
| **F8**  | Seguridad — datos sensibles, secretos y logs        | Secretos en repo y en historial git, `.env` fuera de control de versiones, PII/salud en logs (`logging_config.py`, `print` en `converse.py`), cifrado en tránsito, retención y borrado, configuración de Atlas                                                                                                    | `backend/app/logging_config.py`, `backend/app/routes/converse.py`, `backend/app/config.py`, `.env.example` (ambos), `docker-compose.yml`, `backend/render.yaml`, `frontend/vercel.json`                                                                          | `gitleaks detect --no-git=false`, `trufflehog`, revisión de logs generados en ejecución local, `grep` de PII en `print`/`logger`, revisión manual de Atlas (requiere acceso)                                                               | **Alta**  | 5–6 h                        |
| **F9**  | Dependencias                                        | Versiones fijadas vs. rangos, CVEs conocidos, dependencias innecesarias, lockfile, cadena de suministro del script offline                                                                                                                                                                                        | `backend/requirements.txt`, `backend/requirements-dev.txt`, `frontend/package.json`, `frontend/package-lock.json`                                                                                                                                                | `pip-audit -r`, `safety`, `npm audit --production`, `npm outdated`, `license-checker`, `trivy fs`                                                                                                                                          | Media     | 3–4 h                        |
| **F10** | Configuración y ejecución                           | Instalación desde cero en máquina limpia; variables de entorno requeridas vs. documentadas; arranque backend/frontend; `docker-compose up`; despliegue Render/Vercel; puertos; scripts de `manage.py`                                                                                                             | `README.md`, `README_V1.2.md`, `backend/main.py`, `backend/.env.example`, `docker-compose.yml`, `frontend/vite.config.ts`, `frontend/package.json`, `backend/render.yaml`, `frontend/vercel.json`                                                                | Ejecución guiada en entorno limpio (venv temporal fuera del proyecto) + `uvicorn` + `npm ci && npm run build` + checklist paso a paso                                                                                                      | Media     | 4–6 h                        |
| **F11** | Pruebas, CI y despliegue                            | Cobertura real, flujos críticos sin prueba (auth, RBAC, IDOR, reporte, dosificación), calidad de los tests, ausencia de CI, escaneos automáticos, separación de entornos y gestión de secretos en Render/Vercel                                                                                                   | `backend/tests/` (6 archivos), `frontend/src/chat/SearchPhase.test.tsx`, `frontend/src/components/ErrorBoundary.test.tsx`, `backend/pytest.ini`, ausencia de `.github/workflows/`                                                                                | `pytest --cov=app --cov-report=term-missing`, `vitest run --coverage`, revisión manual de casos, propuesta de pipeline (lint + test + audit + gitleaks)                                                                                    | Media     | 6–8 h                        |
| **F12** | Rendimiento y consumo                               | Tamaño y composición del bundle, _code splitting_, consultas Mongo sin índice, regex sobre colecciones, carga del catálogo en memoria, generación de reportes, arranque del backend                                                                                                                               | `frontend/vite.config.ts`, `frontend/package.json`, `backend/app/database/mongodb.py`, `backend/app/expert_system/engine.py`, `backend/app/reports/history_document.py`, `backend/app/routes/clinical_history.py`                                                | `npm run build` (analizar salida), `vite-bundle-visualizer`, `mongosh` + `explain("executionStats")`, medición con `time`/`pytest-benchmark`, revisión de índices                                                                          | Baja      | 3–4 h                        |
| **F13** | Documentación y funcionalidades simuladas           | Coherencia entre README raíz, `README_V1.2.md` y el código real; inventario de lo simulado (FHIR R4, ECG, dictado, MFA, cama, firma) y si la UI lo presenta como real; instrucciones reproducibles; comentarios engañosos                                                                                         | `README.md`, `README_V1.2.md`, `DATOS_PRUEBA.md`, `backend/README.md`, `frontend/README.md`, `frontend/src/chat/constants.ts`, `frontend/src/pages/`                                                                                                             | Revisión manual + búsqueda de términos "simulado/mock/placeholder" + verificación funcional en navegador                                                                                                                                   | Media     | 3–4 h                        |
| **F14** | Calidad y mantenibilidad                            | Duplicación, complejidad, código muerto, monolitos de datos, acoplamiento `normalizer`↔`engine`, convenciones, linter/formatter Python ausente, deuda técnica                                                                                                                                                     | `backend/seed_data.py` (6.986), `backend/app/expert_system/normalizer.py` (1.196), `backend/app/reports/history_document.py` (1.322), `backend/app/expert_system/engine.py`, `frontend/src/context/AuthContext.tsx`, `frontend/src/api/client.ts`                | `ruff check`, `ruff format --check`, `mypy --ignore-missing-imports` (informativo), `radon cc -s`, `vulture`, `eslint .`, `tsc --noEmit`, `jscpd`                                                                                          | Baja      | 4–6 h                        |
| **F15** | Licencias y cumplimiento                            | Ausencia de `LICENSE`; licencias de las 39 dependencias; brecha frente a Ley 1581/2012, Res. 1995/1999, Ley 2015/2020, Ley 1751/2015; clasificación INVIMA (software como dispositivo médico); datos reales vs. sintéticos; consentimiento y derechos del titular                                                 | Repo completo, `backend/requirements.txt`, `frontend/package.json`, `DATOS_PRUEBA.md`, `backend/seed_data.py`, `backend/seed_demo.py`, `frontend/src/pages/Login.tsx`                                                                                            | `pip-licenses`, `license-checker --summary`, revisión documental + entrevista con el equipo + **concepto jurídico externo**                                                                                                                | Media     | 4 h + revisión legal         |

### 3.1 Criterio de éxito por fase

| Fase | Se considera superada cuando…                                                                                                                             |
| ---- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| F0   | No quedan archivos huérfanos sin justificar; duplicados de documentación identificados; exclusiones de git correctas.                                     |
| F1   | Existe una matriz de hallazgos con reproducción (request/response) para OTP, JWT y política de contraseña; cada hallazgo tiene severidad y recomendación. |
| F2   | Se demuestra (o se descarta) la suplantación de identidad vía `social-register` con evidencia reproducible.                                               |
| F3   | Matriz completa rol × endpoint × recurso, con veredicto por fila y pruebas automáticas de los casos de acceso cruzado.                                    |
| F4   | Todos los puntos de entrada con datos de usuario están mapeados y clasificados como validados / parcialmente validados / sin validar.                     |
| F5   | Tabla de casos borde del motor y de dosificación, con resultado observado y observación clínica firmada por un profesional.                               |
| F6   | Payloads XSS probados; documento generado y control de acceso al endpoint verificado.                                                                     |
| F7   | Importación probada con archivo válido, inválido, sobredimensionado y con fórmulas; permisos verificados.                                                 |
| F8   | Resultado de `gitleaks` sobre repo e historial; inventario de datos sensibles que aparecen en logs.                                                       |
| F9   | Lista de CVEs y licencias por dependencia, con acción recomendada por hallazgo.                                                                           |
| F10  | Checklist de instalación ejecutada de punta a punta, con los pasos que fallan documentados.                                                               |
| F11  | Cobertura medida por módulo y lista priorizada de pruebas faltantes; pipeline de CI propuesto.                                                            |
| F12  | Línea base de bundle y de tiempos de las 3 consultas más costosas, con cuello de botella identificado.                                                    |
| F13  | Inventario cerrado de funcionalidades simuladas y veredicto de si la UI induce a engaño.                                                                  |
| F14  | Lista de deuda técnica priorizada por impacto/esfuerzo, con métricas objetivas (complejidad, duplicación).                                                |
| F15  | Tabla de brechas normativas con estado y responsable de cierre; pendiente de validación jurídica.                                                         |

### 3.2 Automatizable vs. manual

| Automatizable                                                                                                                                                           | Manual / requiere criterio humano                                                                                                                                                                                                                     |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `bandit`, `semgrep`, `gitleaks`, `pip-audit`, `npm audit`, `license-checker`, `ruff`, `eslint`, `tsc`, `pytest --cov`, `vitest --coverage`, `radon`, `vulture`, `trivy` | Lógica clínica del motor y dosificación; avisos y UX de "herramienta de apoyo"; inventario de simulado vs. real; control de acceso por propiedad del recurso (requiere entender el modelo de negocio); redacción de hallazgos; cumplimiento normativo |

---

## 4. Riesgos preliminares detectados

> Indicios verificados en lectura de código. La explotación no se ejecutó en esta fase.

### Críticos

| ID   | Riesgo                                                                                                                                                                                                                                       | Archivo / línea                                                | Evidencia                                                                                                                               | Tipo    |
| ---- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- | ------- |
| R-01 | **Suplantación de identidad en registro social**: el backend valida el token de Google pero **descarta el perfil devuelto** y usa el `email`/`name` enviados por el cliente. Con un token propio válido se puede registrar cualquier correo. | `backend/app/routes/auth.py:313-336` (uso en 319-320, 325-326) | `await verify_social_token(provider, token)` sin asignar el retorno; luego `db.users.find_one({"email": email})` con el email del body. | [HECHO] |
| R-02 | **Clave JWT por defecto**: si falta `JWT_SECRET` en el entorno, la app arranca y firma tokens con un valor conocido incluido en el repo → falsificación de sesiones de cualquier rol.                                                        | `backend/app/config.py:8`                                      | `JWT_SECRET = os.getenv("JWT_SECRET", "mimetic-ai-****tion")` (valor enmascarado).                                                      | [HECHO] |
| R-03 | **Fuga del código de verificación**: el endpoint de prueba devuelve el OTP en la respuesta, anulando la verificación por correo.                                                                                                             | `backend/app/routes/auth.py:57-65`                             | Línea 65: `return {..., "code_preview": code}`.                                                                                         | [HECHO] |
| R-04 | **Toma de control de cuentas no verificadas**: al registrarse con un email ya existente pero no verificado, se **sobrescriben todos los datos y el `password_hash`** sin probar posesión del correo.                                         | `backend/app/routes/auth.py:73-105`                            | Líneas 82-97: `update_one` con `$set` de datos personales y `password_hash`.                                                            | [HECHO] |

### Altos

| ID   | Riesgo                                                                                                                                                                            | Archivo / línea                                                                                                                | Evidencia                                                                                    | Tipo    |
| ---- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------- | ------- |
| R-05 | **Fuerza bruta sobre OTP de 6 dígitos**: `/verify-email` no tiene límite de intentos ni bloqueo; el código se genera con un PRNG no criptográfico y no se invalida tras N fallos. | `backend/app/routes/auth.py:98,133,144-169`                                                                                    | `str(random.randint(100000, 999999))`; comparación directa en 158; sin contador de intentos. | [HECHO] |
| R-06 | **Inyección de regex en búsqueda**: el término de búsqueda se interpola en `$regex` sin escapar ni limitar longitud → ReDoS y extracción de datos por patrones.                   | `backend/app/routes/clinical_history.py:97,111`                                                                                | `{"document_number": {"$regex": regex}}` construido a partir del parámetro de query.         | [HECHO] |
| R-07 | **Token en `localStorage`**: cualquier XSS permite exfiltrar la sesión; no hay cookie `HttpOnly` ni rotación.                                                                     | `frontend/src/api/client.ts:8`; `frontend/src/context/AuthContext.tsx:69,82`                                                   | `localStorage.getItem('token')` / `setItem('token', ...)`.                                   | [HECHO] |
| R-08 | **Fuga de detalles internos al cliente**: el endpoint conversacional devuelve `str(e)` en la respuesta al usuario.                                                                | `backend/app/routes/converse.py:237`                                                                                           | `reply=f"Error interno: {str(e)}"`.                                                          | [HECHO] |
| R-09 | **MongoDB local sin autenticación y publicado en todas las interfaces**: el contenedor expone `27017` sin usuario ni contraseña.                                                  | `docker-compose.yml:7-8`                                                                                                       | `ports: "27017:27017"`, sin `MONGO_INITDB_ROOT_USERNAME`.                                    | [HECHO] |
| R-10 | **Ausencia de bitácora de auditoría de accesos**: no existe registro de quién consultó/modificó una historia clínica; solo un comentario sobre metadatos en el pipeline.          | `backend/app/routes/clinical_history.py`, `backend/app/routes/patient_portal.py`; `backend/app/data_treatment/pipeline.py:208` | Búsqueda de `audit` sin coincidencias funcionales.                                           | [HECHO] |

### Medios

| ID   | Riesgo                                                                                                                                                                                            | Archivo / línea                                                          | Evidencia                                                                           | Tipo                               |
| ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------ | ----------------------------------------------------------------------------------- | ---------------------------------- |
| R-11 | **Sin cabeceras de seguridad** (CSP, HSTS, `X-Frame-Options`, `Referrer-Policy`) en backend ni en el hosting estático.                                                                            | `backend/main.py:68-71`; `frontend/vercel.json`                          | Solo `CORSMiddleware` y `LogContextMiddleware`; `vercel.json` sin bloque `headers`. | [HECHO]                            |
| R-12 | **CORS con credenciales y comodines**: `allow_credentials=True` junto con `allow_methods=["*"]` y `allow_headers=["*"]`.                                                                          | `backend/main.py:70`                                                     | Línea citada.                                                                       | [HECHO]                            |
| R-13 | **Validación de entrada laxa**: `email: str` (no `EmailStr`), `password: str` sin longitud mínima ni complejidad, ausencia de `extra="forbid"`, y endpoints que reciben `data: dict` sin esquema. | `backend/app/models/user.py:34-59`; `backend/app/routes/auth.py:289,315` | Modelos sin `Field(...)` ni validadores; firmas `data: dict`.                       | [HECHO]                            |
| R-14 | **Catálogo clínico generado por IA sin validación**: el script offline puede poblar enfermedades/tratamientos generados por LLM sin revisión médica registrada.                                   | `backend/ai_generate_knowledge.py`                                       | Lee claves desde entorno (correcto), pero no hay paso de aprobación clínica.        | [HECHO] / [INDICIO] sobre uso real |
| R-15 | **Dosificación sin validación clínica documentada**: reglas de ajuste por peso/edad/alergia/embarazo sin trazabilidad de fuente ni pruebas de casos límite.                                       | `backend/app/data_treatment/*.py`, `backend/app/expert_system/engine.py` | Falta tabla de casos y verificación por profesional.                                | [INDICIO]                          |
| R-16 | **Cobertura de rate limiting muy baja**: solo 6 de 48 endpoints tienen `@limiter.limit`.                                                                                                          | `backend/app/routes/auth.py:69,145,250,288,314`; `diagnosis.py:60`       | 48 decoradores `@router.*` vs. 6 `@limiter.limit`.                                  | [HECHO]                            |
| R-17 | **Configuración de despliegue apuntando a otro repositorio**: el despliegue de Render no corresponde a este proyecto.                                                                             | `backend/render.yaml:5`                                                  | `repo: https://github.com/SUBHWEI/mimetic-ai`.                                      | [HECHO]                            |

### Bajos

| ID   | Riesgo                                                               | Archivo / línea                                                  | Evidencia                                  | Tipo    |
| ---- | -------------------------------------------------------------------- | ---------------------------------------------------------------- | ------------------------------------------ | ------- |
| R-18 | Monolito de datos en código: 6.986 líneas de catálogo clínico.       | `backend/seed_data.py`                                           | Conteo de líneas.                          | [HECHO] |
| R-19 | Sin CI ni linter/formatter de Python; pruebas solo manuales.         | ausencia de `.github/workflows/`; `backend/` sin `ruff`/`flake8` | Estructura del repo.                       | [HECHO] |
| R-20 | Sin archivo `LICENSE` → por defecto "todos los derechos reservados". | raíz de `Mimetic_V._1.2/` y del repo                             | Búsqueda sin resultados.                   | [HECHO] |
| R-21 | Clave de API en _query string_ (queda en logs de proxy).             | `backend/ai_generate_knowledge.py:71-72`                         | `f"...:generateContent?key={api_key}"`.    | [HECHO] |
| R-22 | Rewrite SPA que colapsa todas las rutas a `/`.                       | `frontend/vercel.json:7-8`                                       | `{"source": "/(.*)", "destination": "/"}`. | [HECHO] |

---

## 5. Brecha de cumplimiento normativo preliminar

> Estado **aparente**, basado en revisión documental y de código. No constituye concepto legal. Vigencia y alcance deben confirmarse con asesoría jurídica.

| Norma / requisito                                                                                                | Estado aparente                  | Observación                                                                                                                                                                                                              |
| ---------------------------------------------------------------------------------------------------------------- | -------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Ley 1581 de 2012** y Decreto 1377 de 2013 — autorización, aviso y política de privacidad, derechos del titular | **No cumple**                    | `frontend/src/pages/Login.tsx:533` muestra "La política de privacidad se publicará antes del despliegue". No hay documento de política, ni flujo de autorización previa, ni mecanismo de acceso/rectificación/supresión. |
| **Ley 1581 de 2012, art. 6** — datos sensibles (salud) requieren consentimiento explícito y medidas reforzadas   | **No cumple**                    | No se encontró consentimiento explícito en el registro ni en la atención; token de sesión en `localStorage` (`frontend/src/api/client.ts:8`).                                                                            |
| **Resolución 1995 de 1999** — historia clínica: contenido mínimo, custodia, confidencialidad                     | **Parcial**                      | Existe estructura de historia (`backend/app/models/clinical_history.py`) y reporte imprimible (`backend/app/reports/history_document.py`), pero no hay bitácora de acceso ni reglas de retención/conservación.           |
| **Ley 2015 de 2020** — historia clínica electrónica e interoperabilidad                                          | **Parcial / no verificable**     | FHIR R4 está declarado como simulado en `README_V1.2.md`; no hay interoperabilidad real.                                                                                                                                 |
| **Ley 1751 de 2015** — derecho a la información y autonomía del paciente                                         | **Parcial**                      | Existe portal del paciente (`backend/app/routes/patient_portal.py`, 5 endpoints), pero sin trazabilidad de quién consultó la información.                                                                                |
| **Ley 23 de 1981** — ética médica y deber de confidencialidad                                                    | **No verificable**               | Depende de la validación clínica y del uso real; el código no puede demostrarlo.                                                                                                                                         |
| **INVIMA / software como dispositivo médico** (sugiere diagnóstico y dosis)                                      | **No verificable**               | Requiere concepto regulatorio. El sistema emite diagnósticos diferenciales y ajustes de dosis, lo que puede ubicarlo en zona regulada. No hay evidencia de clasificación ni de expediente técnico.                       |
| **HIPAA (EE. UU.) / GDPR (UE)**                                                                                  | **No aplica**                    | No hay indicios de pacientes ni operación en esas jurisdicciones. Se usan solo como referencia técnica de buenas prácticas.                                                                                              |
| **ISO/IEC 27001 / IEC 62304**                                                                                    | **No aplica** como certificación | Proyecto académico sin SGSI ni ciclo de vida de software médico formal. Útiles como marco de referencia para F1–F11.                                                                                                     |
| **Datos reales vs. datos de prueba**                                                                             | **Parcial**                      | `DATOS_PRUEBA.md` documenta credenciales demo y `backend/seed_demo.py` siembra datos sintéticos; no se hallaron indicios de datos reales en el repo. Confirmación plena requiere revisar la base de demo desplegada.     |
| **Licencias**                                                                                                    | **No cumple**                    | No hay `LICENSE` en el repo (R-20). Dependencias de backend y frontend son permisivas por nombre (MIT/Apache-2.0/BSD), sin escaneo formal.                                                                               |
| **Licencias de recursos incluidos**                                                                              | **No aplica**                    | No hay material de terceros: solo `frontend/public/logo.png` (marca propia) y diagramas propios.                                                                                                                         |

---

## 6. Elementos que requieren validación externa

| Tipo                | Elemento                                                                                                              | Quién debe validar                                     | Por qué no puede cerrarlo la auditoría técnica                                                                                                   |
| ------------------- | --------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Clínica**         | Pesos IDF, cobertura y especificidad del motor (`backend/app/expert_system/engine.py`)                                | Médico con experiencia en urgencias / medicina interna | La auditoría verifica consistencia lógica, no corrección clínica.                                                                                |
| **Clínica**         | Reglas de dosificación por peso/edad, máximos, contraindicaciones, alergias, embarazo (`backend/app/data_treatment/`) | Médico y/o químico farmacéutico                        | Requiere criterio farmacológico y contraste con guías vigentes.                                                                                  |
| **Clínica**         | Contenido del catálogo (51 enfermedades, 276 síntomas, 51 tratamientos) y origen de cada registro                     | Comité clínico                                         | Puede haber contenido generado por LLM sin revisión (`backend/ai_generate_knowledge.py`).                                                        |
| **Clínica**         | Redacción y ubicación de los avisos de "herramienta de apoyo, no sustituye el criterio médico"                        | Médico + UX                                            | Verificar que el aviso sea visible y no ambiguo (hay indicios en `backend/app/routes/report.py:105` y `frontend/src/chat/HistoryPhase.tsx:656`). |
| **Legal**           | Clasificación INVIMA (software como dispositivo médico)                                                               | Abogado regulatorio / asesor INVIMA                    | Decisión jurídica, no técnica.                                                                                                                   |
| **Legal**           | Cumplimiento de Ley 1581/2012: política de privacidad, autorización, derechos del titular                             | Abogado de protección de datos                         | Requiere revisión de documentos y procesos, no solo de código.                                                                                   |
| **Legal**           | Texto de consentimiento informado y términos de uso                                                                   | Abogado + comité de ética                              | No existe hoy en el proyecto.                                                                                                                    |
| **Legal**           | Licencia del proyecto y titularidad del código de los estudiantes                                                     | Institución / asesor legal                             | Depende de reglamento de propiedad intelectual de UNIMINUTO.                                                                                     |
| **Infraestructura** | Configuración de MongoDB Atlas: usuarios, roles, lista blanca de IP, backups, cifrado en reposo                       | Responsable de infraestructura con acceso a Atlas      | No hay acceso a la nube desde esta auditoría.                                                                                                    |
| **Infraestructura** | Variables de entorno y secretos en Render y Vercel; separación de entornos                                            | Responsable de despliegue                              | No verificable sin acceso a los paneles.                                                                                                         |
| **Infraestructura** | Entrega y reputación de correo (Gmail API / SMTP / SendGrid) y pantalla de consentimiento OAuth                       | Responsable de integraciones                           | Requiere credenciales y prueba real de envío.                                                                                                    |
| **Infraestructura** | Certificados TLS, DNS y cabeceras efectivas en producción                                                             | Responsable de despliegue                              | Solo medible sobre el dominio desplegado.                                                                                                        |

---

## 7. Checklist de avance

### Preparación

- [ ] F0 — Inventario y árbol del proyecto confirmados
- [ ] F0 — Exclusiones verificadas (`node_modules`, `dist`, `__pycache__`, `.pytest_cache`, `.env`)
- [ ] F0 — Archivos huérfanos y duplicados de documentación listados

### Seguridad (prioridad máxima)

- [ ] F1 — Flujo de registro y política de contraseña revisados
- [ ] F1 — Generación, expiración, reintentos y almacenamiento del OTP verificados
- [ ] F1 — Fuerza bruta y enumeración de usuarios probadas
- [ ] F1 — Manejo de JWT (algoritmo, expiración, revocación, refresh) documentado
- [ ] F1 — Almacenamiento del token en frontend y riesgo XSS evaluados
- [ ] F2 — Validación del token de Google en backend verificada
- [ ] F2 — Vinculación de cuentas y rol por defecto revisados
- [ ] F2 — Prueba de suplantación en `social-register` ejecutada
- [ ] F3 — Matriz rol × endpoint × recurso completada (48 endpoints)
- [ ] F3 — Casos de IDOR/BOLA entre pacientes, médicos y hospitales probados
- [ ] F3 — Escalada de privilegios y creación de admin/super_admin probada
- [ ] F4 — Inyección NoSQL (`$ne`, `$regex`, `$where`) probada en todos los filtros
- [ ] F4 — Modelos Pydantic auditados (tipos, longitudes, `extra`)
- [ ] F6 — XSS en reporte HTML probado con datos del paciente
- [ ] F6 — Control de acceso al documento generado verificado
- [ ] F7 — Importación de catálogo probada con archivos inválidos y sobredimensionados
- [ ] F8 — `gitleaks` ejecutado sobre repo e historial git
- [ ] F8 — Inventario de datos sensibles en logs completado

### Dominio clínico

- [ ] F5 — Casos borde del motor de diagnóstico documentados
- [ ] F5 — Cálculo de dosis revisado (unidades, redondeos, máximos, nulos)
- [ ] F5 — Alergias, embarazo y comorbilidades probados
- [ ] F5 — Trazabilidad de la sugerencia evaluada
- [ ] F5 — Validación clínica firmada por profesional de salud

### Dependencias y ejecución

- [ ] F9 — `pip-audit` y `npm audit` ejecutados sin hallazgos abiertos
- [ ] F9 — Licencias de las 39 dependencias inventariadas
- [ ] F10 — Instalación desde cero reproducida en entorno limpio
- [ ] F10 — `docker-compose up` y conexión a Mongo verificadas
- [ ] F10 — Variables de entorno documentadas vs. requeridas conciliadas

### Calidad, pruebas y documentación

- [ ] F11 — Cobertura backend y frontend medida
- [ ] F11 — Pruebas faltantes de flujos críticos priorizadas
- [ ] F11 — Pipeline de CI propuesto (lint + tests + audit + secretos)
- [ ] F12 — Línea base de bundle y de consultas Mongo registrada
- [ ] F13 — Inventario de funcionalidades simuladas cerrado
- [ ] F13 — Verificado que la UI no presenta lo simulado como real
- [ ] F14 — Deuda técnica priorizada por impacto/esfuerzo
- [ ] F14 — `ruff`, `eslint`, `tsc` y `vulture` ejecutados

### Cumplimiento

- [ ] F15 — Brecha frente a Ley 1581/2012 documentada
- [ ] F15 — Brecha frente a Res. 1995/1999 y Ley 2015/2020 documentada
- [ ] F15 — Clasificación INVIMA consultada
- [ ] F15 — Confirmado que no hay datos reales de pacientes
- [ ] F15 — Recomendación de `LICENSE` y de política de privacidad emitida

---

## 8. Próximos pasos recomendados

**Ruta rápida (1 día, alto impacto):** F0 → F8 → F1 → F2.
Cierra los cuatro riesgos críticos (R-01 a R-04), detecta secretos y establece la línea base de seguridad. Es lo que permite decir con evidencia si el sistema puede o no recibir datos reales.

**Orden sugerido de ejecución:**

1. **F0** — Higiene e inventario (base para todo lo demás).
2. **F8** — Secretos y datos sensibles (rápido, evita filtrar información durante el resto de la auditoría).
3. **F1** — Autenticación, OTP y JWT.
4. **F2** — Google OAuth (hallazgo crítico independiente).
5. **F3** — RBAC, IDOR y escalada (el riesgo más costoso en un sistema de salud).
6. **F4** — Inyección NoSQL y validación de entrada.
7. **F6** — Reporte HTML e historia clínica.
8. **F5** — Motor y dosificación (requiere agendar al profesional clínico desde el inicio; es la fase con más dependencia externa).
9. **F7** — Importación de catálogo.
10. **F9** — Dependencias y cadena de suministro.
11. **F10** — Instalación y ejecución desde cero.
12. **F11** — Pruebas y CI.
13. **F13** — Documentación y funcionalidades simuladas.
14. **F12** — Rendimiento (solo si hay intención de piloto con usuarios).
15. **F14** — Mantenibilidad y deuda técnica.
16. **F15** — Licencias y cumplimiento (en paralelo desde el día 1, porque depende de terceros).
