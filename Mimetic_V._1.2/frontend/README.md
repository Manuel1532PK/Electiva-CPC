# MIMETIC — Frontend

Interfaz clínica del sistema experto de diagnóstico médico. **React + Vite + TypeScript** desplegada en Vercel.

## Inicio rápido

```bash
npm install
npx vite --port 5173
```

Variables de entorno (`.env` en la raíz del frontend):

| Variable | Uso |
|----------|-----|
| `VITE_API_URL` | URL del backend (en dev `http://localhost:8001`; en Vercel la del backend de Render) |

> `vite.config.ts` ya define el proxy `/api` → `http://localhost:8001` en desarrollo.

## Estructura

```
src/
├── api/
│   └── client.ts            # Cliente HTTP central (JWT, FormData/multipart, manejo 401/403)
├── auth/
│   └── AuthContext.tsx      # Sesión, roles, verificación de correo pendiente
├── components/
│   ├── admin/
│   │   ├── ExpertSystemImport.tsx   # Importación del catálogo (super_admin)
│   │   ├── UserManagement.tsx
│   │   └── HospitalManagement.tsx
│   ├── chat/                # Componentes del chat de diagnóstico por fases
│   └── ...
├── pages/
│   ├── AdminPanel.tsx       # Panel con pestañas (solo admin/super_admin)
│   ├── Register.tsx         # Registro con cascada País/Departamento/Ciudad
│   ├── Login.tsx
│   ├── PatientDashboard.tsx
│   └── ...
└── App.tsx                  # React Router + rutas protegidas por rol
```

## Rutas principales

| Ruta | Acceso | Vista |
|------|--------|-------|
| `/` | público | Login (correo o Google) |
| `/register` | público | Registro con verificación de correo (6 dígitos) |
| `/admin` | `admin` / `super_admin` | Panel de administración |
| `/chat` | `medico` | Chat de diagnóstico conversacional |
| `/paciente` | `paciente` | Dashboard del paciente |
| `/share/:id` | público | Compartir historia clínica |

## Panel de administración (`/admin`)

Pestañas visibles según rol:

| Pestaña | Visibilidad | Descripción |
|---------|-------------|-------------|
| **Usuarios** | `admin` / `super_admin` | CRUD de usuarios, crear cuentas |
| **Hospitales** | `admin` / `super_admin` | CRUD de hospitales |
| **Sistema experto** | `super_admin` (único) | Importar catálogo (symptoms/diseases/treatments) desde CSV/Excel/JSON a MongoDB Atlas |

## Compilación y checks

```bash
npm run build      # tsc + vite build (type-safe)
npm run test       # vitest
npm run lint       # eslint
```

## Despliegue (Vercel)

1. Subir el repo en Vercel → framework preset **Vite**.
2. Configurar `VITE_API_URL` apuntando al backend (Render).
3. Build command: `npm run build` · Output dir: `dist`.
