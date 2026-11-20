# Plan de despliegue — Backend (Render)

**Rama de producción:** `produccion-backend`
**Repositorio:** `https://github.com/Manuel1532PK/Electiva-CPC.git`
**Directorio de la aplicación:** `Mimetic_V._1.2/backend`
**Servicio Render:** `mimetic-ai-api`
**URL de producción:** `https://mimetic-ai-api.onrender.com`
**Frontend consumidor:** `https://mimetic-ai.vercel.app` (desplegado desde la rama `produccion-frontend`)
**Fecha:** 2026-11-19

---

## 1. Alcance y supuestos

Este plan cubre únicamente el **backend** (FastAPI + Motor/MongoDB). El frontend se despliega por separado en Vercel siguiendo `Docs/prompt/planFrontend.md` de la rama `produccion-frontend`.

Supuestos:

- Existe una cuenta de Render con acceso al repositorio de GitHub.
- Existe una instancia de MongoDB Atlas accesible públicamente (o desde Render).
- Los valores sensibles se cargan como variables de entorno en Render; nunca se versionan.

## 2. Requisitos previos

| Elemento | Valor |
|---|---|
| Python | **3.11.11** (definido en `.python-version` y `runtime.txt`; Render usa `.python-version`) |
| Dependencias | `requirements.txt` (runtime) y `requirements-dev.txt` (solo pruebas) |
| Base de datos | MongoDB Atlas + cadena `MONGODB_URL` |
| Rama | `produccion-backend` |

> Nota verificada: en este PC las pruebas pasan con Python 3.13, pero con Python 3.14 falla la instalación de `pydantic-core==2.23.x` (sin wheel y sin compilador MSVC). Usar 3.11.11 o 3.13 para desarrollo local; Render usará 3.11.11.

## 3. Verificación local antes de desplegar

```bash
git checkout produccion-backend
cd Mimetic_V._1.2/backend
py -3.11 -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt -r requirements-dev.txt
pytest -q
```

Resultado esperado verificado en este repositorio: **59 pruebas pasadas**.

## 4. Creación del servicio en Render

### 4.1 Opción recomendada: Blueprint

1. En Render: **New → Blueprint**.
2. Conectar el repo `Manuel1532PK/Electiva-CPC` y seleccionar la rama `produccion-backend`.
3. En **Blueprint Path** indicar: `Mimetic_V._1.2/backend/render.yaml`.
   > Render busca `render.yaml` en la raíz por defecto; por eso hay que especificar esta ruta al crear el Blueprint.
4. Render mostrará un único servicio web: `mimetic-ai-api`. Revisar la configuración y confirmar.

### 4.2 Configuración declarada en `render.yaml`

| Campo | Valor |
|---|---|
| `type` | `web` |
| `name` | `mimetic-ai-api` |
| `runtime` | `python` |
| `repo` | `https://github.com/Manuel1532PK/Electiva-CPC.git` |
| `branch` | `produccion-backend` |
| `rootDir` | `Mimetic_V._1.2/backend` |
| `plan` | `free` (suficiente para la electiva; considerar `0.5c-512mb` si se requiere menos sleep) |
| `buildCommand` | `pip install -r requirements.txt` |
| `startCommand` | `uvicorn main:app --host 0.0.0.0 --port $PORT` |
| `healthCheckPath` | `/health` |
| `autoDeployTrigger` | `commit` |

> El archivo anterior apuntaba a otro repositorio (`SUBHWEI/mimetic-ai`) y a `rootDir: backend`; fue corregido en esta rama.

Si se prefiere crear el servicio manualmente (**Web Service → Python**), usar exactamente los mismos valores de repo, rama, Root Directory, build y start command.

## 5. Variables de entorno

Configurar en el servicio de Render (los campos con `sync: false` se piden al crear el Blueprint):

| Variable | Valor | Obligatoria | Observación |
|---|---|---|---|
| `PYTHON_VERSION` | `3.11.11` | Sí | Fija la versión; también existe `.python-version` dentro de `rootDir` |
| `MONGODB_URL` | `mongodb+srv://...` | **Sí** | Cadena de MongoDB Atlas. Sin ella `/health` responde `degraded` |
| `MONGODB_DB_NAME` | `mimetic_ai` | No | Nombre de la base de datos |
| `JWT_SECRET` | valor aleatorio largo | **Sí en producción** | No dejar el valor por defecto `mimetic-ai-secret-change-in-production` |
| `JWT_ALGORITHM` | `HS256` | No | |
| `JWT_EXPIRATION_HOURS` | `24` | No | |
| `CORS_ORIGINS` | `https://mimetic-ai.vercel.app` | **Sí** | Debe incluir el dominio exacto del frontend; separar varios con comas |
| `LOG_LEVEL` | `INFO` | No | Logging JSON estructurado |
| `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` | credenciales OAuth | No | Login con Google |
| `GMAIL_API_CLIENT_ID` / `GMAIL_API_CLIENT_SECRET` / `GMAIL_API_REFRESH_TOKEN` | credenciales Gmail API | Recomendado | En Render free, SMTP saliente suele estar bloqueado; usar Gmail API por HTTPS |
| `SENDGRID_API_KEY` | clave SendGrid | No | Alternativa de correo |
| `GEMINI_API_KEY` / `OPENAI_API_KEY` / `TOGETHER_API_KEY` | clave del proveedor LLM | No | Motor de diagnóstico; el sistema funciona con reglas si no hay proveedor |

> Para MongoDB Atlas, agregar `0.0.0.0/0` al IP Access List (Render no tiene IP fija en el plan free) o usar una IP estática en planes superiores.

## 6. Verificación post-despliegue

1. `curl https://mimetic-ai-api.onrender.com/health` → HTTP 200 con `"status": "ok"` (o `degraded` si Mongo no conecta) y header `X-Request-ID`.
2. Abrir `https://mimetic-ai-api.onrender.com/docs` y comprobar Swagger UI.
3. Probar `POST /api/auth/register` y `POST /api/auth/login` con un usuario de prueba.
4. Desde el frontend en Vercel, confirmar que login y chat consultan la API sin errores CORS.
5. Revisar los logs en Render Dashboard → *Logs* y verificar que no hay excepciones en el arranque.
6. Si el plan free está suspendido, la primera petición puede tardar ~30–60 s (cold start); esperar antes de darlo por fallido.

## 7. Rollback

- **Desde Render:** pestaña *Deploys* del servicio → seleccionar un deploy exitoso anterior → **Redeploy**.
- **Desde Git:** revertir el commit en `produccion-backend` y hacer push; Render disparará un deploy automático (`autoDeployTrigger: commit`).

Tras el rollback, repetir la sección 6.

## 8. Pruebas unitarias incluidas

| Archivo | Casos cubiertos |
|---|---|
| `tests/test_health_endpoint.py` | `/health` con MongoDB sembrado y logging JSON con `request_id`; estado `degraded` cuando Mongo no conecta |
| `tests/test_logging_config.py` | Formateador estructurado y niveles de log |
| `tests/test_matcher.py` | Motor de coincidencia de síntomas/diagnósticos |
| `tests/test_mongodb_reconnect.py` | Reconexión Motor y ping real |
| `tests/test_normalization.py` | Normalización estricta (minúsculas, sin diacríticos) |
| `tests/test_pytest_helpers.py` | Utilidades de prueba |

Ejecución: `cd Mimetic_V._1.2/backend && pytest -q`. Resultado actual: **59/59 en verde** (con Python 3.13 en este PC; Render usa 3.11.11).

## 9. Riesgos y recomendaciones

- **Versión de Python:** si se elimina `.python-version`, Render usaría Python 3.14 por defecto y la instalación fallaría con las versiones fijadas de `pydantic`. Mantener el archivo y `PYTHON_VERSION=3.11.11`.
- **Plan free:** el servicio se duerme por inactividad. Para una demo, avisar al equipo; para producción real, subir a `0.5c-512mb`.
- **Correo:** SMTP no funciona en Render free; usar Gmail API o SendGrid.
- **CORS/JWT:** son las causas más comunes de fallos después del despliegue; verificarlos antes de probar flujos clínicos.
- **Secretos:** `JWT_SECRET` y credenciales externas solo en Render; el repositorio incluye `.env.example` como plantilla.
