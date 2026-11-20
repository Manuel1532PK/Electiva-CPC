# Plan de despliegue — Frontend (Vercel)

**Rama de producción:** `produccion-frontend`
**Repositorio:** `https://github.com/Manuel1532PK/Electiva-CPC.git`
**Directorio de la aplicación:** `Mimetic_V._1.2/frontend`
**URL de producción:** `https://mimetic-ai.vercel.app`
**API consumida:** `https://mimetic-ai-api.onrender.com` (servicio desplegado desde la rama `produccion-backend`)
**Fecha:** 2026-11-19

---

## 1. Alcance y supuestos

Este plan cubre únicamente el **frontend** (React + Vite + TypeScript). El backend se despliega por separado en Render siguiendo `Docs/prompt/planBackend.md` de la rama `produccion-backend`.

Se asume que:

- El repositorio ya está importado en Vercel con acceso del equipo.
- El backend Render ya responde en `https://mimetic-ai-api.onrender.com/health`.
- No se almacenan secretos en el repositorio; los valores sensibles se configuran en el panel de Vercel.

## 2. Requisitos previos

| Elemento | Valor / recomendación |
|---|---|
| Node.js | 22.22.2+ o 24.15+ (jsdom 30 lo requiere). En Vercel usar la versión por defecto de Node 24 |
| npm | 11.x |
| Cuenta Vercel | Con permisos sobre el repositorio de GitHub |
| Rama | `produccion-frontend` (creada localmente desde `origin/main`) |

## 3. Verificación local antes de desplegar

```bash
git checkout produccion-frontend
cd Mimetic_V._1.2/frontend
npm ci
npm run build
npm test
npm run lint
```

Resultado esperado verificado en este repositorio:

- `npm ci`: dependencias instaladas correctamente (advertencia `EBADENGINE` de `jsdom@30` si Node < 22.22.2; no bloquea).
- `npm run build`: compila con `tsc -b` y genera `dist/` (advertencia de chunks > 500 kB, no bloquea).
- `npm test`: **2 archivos, 6 pruebas, 6 pasadas**.
- `npm run lint`: sin errores de ESLint.

## 4. Configuración del proyecto en Vercel

1. En Vercel: **Add New → Project** e importar `Manuel1532PK/Electiva-CPC`.
2. **Production Branch:** `produccion-frontend`.
3. **Root Directory:** `Mimetic_V._1.2/frontend`.
   > Paso crítico: el `package.json` está dentro de esa carpeta. Si Root Directory queda en la raíz del repo, Vercel no encuentra el proyecto.
4. **Framework Preset:** `Vite` (detectado automáticamente).
5. **Build & Output Settings:**

   | Campo | Valor |
   |---|---|
   | Install Command | `npm ci` |
   | Build Command | `npm run build` |
   | Output Directory | `dist` |

   Estos valores también están declarados en `Mimetic_V._1.2/frontend/vercel.json`, junto con la reescritura SPA `/(.*) → /` para que las rutas de React Router (`/admin`, `/chat`, `/paciente`, `/share/:id`) no devuelvan 404 al recargar.

6. **Deploy** y esperar a que el pipeline finalice.

## 5. Variables de entorno

Configurar en **Project Settings → Environment Variables** para Production, Preview y Development:

| Variable | Valor | Observación |
|---|---|---|
| `VITE_API_URL` | `https://mimetic-ai-api.onrender.com` | Debe apuntar al backend Render. `src/config.ts` usa este mismo valor por defecto en producción si la variable no existe, pero se recomienda declararla explícitamente |

> No incluir `VITE_API_URL` con `http://localhost:8001` en Production: en dev el proxy de `vite.config.ts` redirige `/api` a `127.0.0.1:8001`, pero en el bundle de producción no existe ese proxy.

## 6. Verificación post-despliegue

1. Abrir `https://mimetic-ai.vercel.app` y comprobar que carga la pantalla de login.
2. Navegar directamente a `/register`, `/admin`, `/chat`, `/paciente`: ninguna debe devolver 404 (rewrite SPA).
3. En DevTools → Network, confirmar que las peticiones a `/api/...` salen hacia `https://mimetic-ai-api.onrender.com`.
4. Probar login con un usuario `admin` y verificar que el panel carga datos del backend.
5. Confirmar que no hay errores CORS en consola. Si aparecen, el backend debe incluir `https://mimetic-ai.vercel.app` en `CORS_ORIGINS` (ver plan de backend).
6. Revisar los logs de la función en Vercel ante cualquier error 5xx.

## 7. Rollback

- **Desde Vercel:** pestaña *Deployments* → seleccionar un deployment anterior exitoso → **Promote to Production**.
- **Desde Git:** revertir el commit problemático en `produccion-frontend` y hacer push; Vercel disparará un nuevo deploy automático.

Tras cualquier rollback, repetir la sección 6.

## 8. Pruebas unitarias incluidas

| Archivo | Casos cubiertos |
|---|---|
| `src/chat/SearchPhase.test.tsx` | Propagación del documento buscado, selección de paciente desde resultados, aviso "no se encontraron pacientes", botón "registrar nuevo paciente" (4 pruebas) |
| `src/components/ErrorBoundary.test.tsx` | Render del fallback ante error de un hijo, render normal sin error (2 pruebas) |

Ejecución: `cd Mimetic_V._1.2/frontend && npm test`. Resultado actual: **6/6 en verde**.

## 9. Riesgos y recomendaciones

- **Cold start / bundles grandes:** el build genera un chunk de ~8 MB. No bloquea el despliegue, pero se recomienda aplicar *code splitting* (lazy imports) en una iteración posterior.
- **Node local:** si se usa Node 24.13, `jsdom@30` avisa de versión no soportada; usar Node ≥ 24.15 para eliminar la advertencia.
- **CORS:** el backend debe tener el dominio exacto de Vercel en `CORS_ORIGINS`; de lo contrario el frontend cargará pero las llamadas API fallarán.
- **Secretos:** nunca subir `.env` al repositorio; usar solo `.env.example` como plantilla.
