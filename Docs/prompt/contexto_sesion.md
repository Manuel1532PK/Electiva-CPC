# Contexto de la sesión — MIMETIC v1.2

**Fecha:** 2026-11-20  
**Repositorio:** `https://github.com/Manuel1532PK/Electiva-CPC.git`  
**Ramas de producción:** `produccion-backend`, `produccion-frontend`  
**Servidor MCP de contexto:** `context` (`@modelcontextprotocol/server-memory`)

---

## 1. Objetivo general

Actualizar y desplegar MIMETIC v1.2 en producción, separando backend y frontend en ramas distintas, y resolver los problemas reportados:

- La base de datos aparecía como “no conectada”.
- Los códigos de verificación de correo no llegaban.
- El portal de médico/paciente no mostraba el diseño actual.
- Se necesitaba una cuenta de médico de prueba en producción.

---

## 2. Estado de Git

| Elemento | Estado |
|---|---|
| `main` | Contiene el commit `49c36da` con los cambios de backend, visual y correo |
| `produccion-backend` local | Commit `59bc66c` |
| `origin/produccion-backend` | Commit `865bbd5` |
| `produccion-frontend` local | Commit `40427eb` |
| `origin/produccion-frontend` | Sincronizado con la rama local |
| `opencode.json` | Archivo de configuración local del MCP, no debe subirse |
| Force push | No se realizó |

---

## 3. Ramas de producción

### `produccion-backend`
- Contiene el backend FastAPI y el plan de despliegue en Render.
- Commit local: `59bc66c`
- Commit equivalente en `main`: `49c36da`
- `origin/produccion-backend` quedó en `865bbd5` por un merge desde `main`.

### `produccion-frontend`
- Contiene el frontend React/Vite y el plan de despliegue en Vercel.
- URL de producción: `https://mimetic-ai-v12.vercel.app`
- API consumida: `https://mimetic-ai-api-v12.onrender.com`
- Commit actual: `40427eb`

---

## 4. Despliegues

### Backend — Render
- **Servicio:** `mimetic-ai-api-v12`
- **URL:** `https://mimetic-ai-api-v12.onrender.com`
- **Health check:** `/health`
- **Estado:** desplegado correctamente.
- **Verificación:** `status: ok`, `database: connected`

### Frontend — Vercel
- **Proyecto:** `mimetic-ai-v12`
- **URL:** `https://mimetic-ai-v12.vercel.app`
- **Root Directory:** `Mimetic_V._1.2/frontend`
- **Production Branch:** `produccion-frontend`
- **Verificación:** HTTP 200.

---

## 5. Correo con Gmail API

- `send_verification_code()` ahora entrega el código de forma **sincrónica**.
- Si no hay proveedor configurado, `POST /api/auth/register` responde `503` en lugar de “enviado”.
- `EMAIL_PROVIDER` soporta:
  - `auto`
  - `gmail_api`
  - `sendgrid`
  - `smtp`
  - `none`
- `setup_gmail_api.py` usa OAuth con **PKCE** y redirect local `http://127.0.0.1:8090/callback`.
- Se verificó entrega real con `mimequack@gmail.com`.
- En Render se configuraron las variables:
  - `EMAIL_PROVIDER=gmail_api`
  - `FROM_EMAIL=MIMETIC <mimequack@gmail.com>`
  - `GMAIL_API_CLIENT_ID`
  - `GMAIL_API_CLIENT_SECRET`
  - `GMAIL_API_REFRESH_TOKEN`

> Los valores secretos no se incluyen en este documento.

---

## 6. Portal del paciente

- Se rediseñó con `src/styles/portal.css`.
- `PatientDashboard.tsx` importa `portal.css` en lugar de `App.css`.
- Diseño verificado:
  - Header moderno con blur.
  - Tarjetas blancas.
  - Pestañas tipo píldora.
  - Línea de tiempo.
  - Modal rediseñado.
  - Responsive en móvil.
- `npm run build` pasa sin errores.
- Consola del navegador sin errores.

---

## 7. Portal del médico

- Usa `ChatApp` y `mimetic.css`, ya con el diseño actual.
- Se creó una cuenta de prueba en producción:
  - **Correo:** `medico.prueba@mimetic.test`
  - **Contraseña:** `Medico123!`
  - **Rol:** `medico`
  - **Base de datos:** `mimetic_ai`
  - **Estado:** verificada y activa.
- Se verificó login y carga del portal en producción.

---

## 8. Planes actualizados

### Backend
- **Archivo:** `Docs/prompt/planBackend.md`
- **Sección nueva:** `10. Actualización 2026-11-20 — Backend`
- **Pruebas:** `65/65 en verde`

### Frontend
- **Archivo:** `Docs/prompt/planFrontend.md`
- **Sección nueva:** `10. Actualización 2026-11-20 — Frontend`
- **Pruebas:** `6/6 en verde`

Ambos planes fueron incluidos en el commit `40427eb` de `produccion-frontend`.

---

## 9. MCP `context`

- Se instaló y configuró el servidor MCP `context` con `@modelcontextprotocol/server-memory`.
- El grafo quedó con:
  - **12 entidades**
  - **11 relaciones**
- Relaciones principales:
  - `MIMETIC v1.2` → `produccion-backend`
  - `MIMETIC v1.2` → `produccion-frontend`
  - `produccion-backend` → `Backend Render`
  - `produccion-frontend` → `Frontend Vercel`
  - `produccion-backend` → `Correo Gmail API`
  - `produccion-frontend` → `Portal del paciente`
  - `produccion-frontend` → `Portal del médico`
  - `produccion-backend` → `Plan Backend`
  - `produccion-frontend` → `Plan Frontend`
  - `Portal del médico` → `Cuenta de médico en producción`

---

## 10. Próximos pasos sugeridos

1. Revisar los planes actualizados con el dueño.
2. Confirmar si se desea mantener `opencode.json` fuera del repositorio.
3. Verificar en producción el envío de un correo real a `mimequack@gmail.com`.
4. Revisar el portal de médico con la cuenta de prueba creada.
5. Si todo está bien, hacer merge de las ramas de producción a `main`.

---

## 11. Notas finales

- No se hizo `force push`.
- No se subieron secretos al repositorio.
- `opencode.json` es configuración local del MCP y no debe versionarse.
- El contexto de esta sesión también quedó guardado en el servidor MCP `context`.
