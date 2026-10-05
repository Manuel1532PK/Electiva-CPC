# Electiva CPC - Sistema Experto MIMETIC AI

Sistema de apoyo al diagnóstico médico con motor de sistema experto, desarrollado como parte de la Electiva CPC. Este proyecto implementa una arquitectura completa con backend en FastAPI, frontend en React/Vite, base de datos MongoDB Atlas y funcionalidades de diagnóstico conversacional asistido por IA.

## Descripción del Proyecto

MIMETIC AI es un sistema conversacional de apoyo al diagnóstico médico que permite a los médicos registrar pacientes, describir síntomas en lenguaje natural y obtener diagnósticos diferenciales con sus respectivos tratamientos. El sistema incluye control del médico sobre diagnósticos y tratamientos, ajuste de dosis por peso/edad/embarazo/alergias y generación de historias clínicas en PDF.

## Tecnologías Utilizadas

### Backend
- **Python 3.11+** - Lenguaje de programación
- **FastAPI** - Framework web para APIs
- **Motor** - Driver asíncrono para MongoDB
- **Pydantic** - Validación de datos
- **Uvicorn** - Servidor ASGI

### Frontend
- **React 18.3.1** - Biblioteca para interfaces de usuario
- **Vite** - Herramienta de construcción
- **TypeScript** - Tipado estático
- **React Router DOM** - Enrutamiento
- **@react-oauth/google** - Autenticación con Google

### Base de Datos
- **MongoDB Atlas** - Base de datos NoSQL en la nube

### Servicios Externos
- **Gmail API / SMTP** - Envío de correos electrónicos
- **SendGrid** - Servicio alternativo de correo
- **Google OAuth 2.0** - Autenticación social
- **Gemini / OpenAI / Together** - Proveedores de IA

## Arquitectura del Sistema

`
Frontend (React/Vite) ←→ Backend (FastAPI) ←→ MongoDB Atlas
                            ↓
                    Gmail API / Gemini / OpenAI / Together
`

## Roles del Sistema

| Rol | Permisos |
|---|---|
| super_admin | Acceso completo al sistema, gestión de usuarios, hospitales y alimentación del catálogo de conocimiento (importación de archivos CSV/Excel/JSON) |
| dmin | Gestión de usuarios y hospitales |
| medico | Chat de diagnóstico, historias clínicas, aprobación/modificación/descartar tratamientos |
| paciente | Consulta de sus diagnósticos y tratamientos |

## Estructura del Proyecto

### Backend (/backend)

`
backend/
├── app/
│   ├── auth/                # Autenticación JWT, OAuth y RBAC
│   ├── config.py            # Configuración y variables de entorno
│   ├── data_treatment/      # Limpieza y entrenamiento del catálogo
│   ├── database/            # Conexión a MongoDB (Motor async)
│   ├── expert_system/       # Motor de diagnóstico (matcher, engine, conversation, normalizer)
│   ├── models/              # Modelos Pydantic
│   ├── routes/              # Endpoints de la API
│   └── utils.py             # Utilidades (normalización de texto)
├── main.py                  # Punto de entrada de la aplicación FastAPI
├── seed_data.py             # Datos iniciales del catálogo
├── requirements.txt         # Dependencias Python
└── README.md                # Documentación específica del backend
`

### Frontend (/frontend)

`
frontend/
├── src/
│   ├── api/                 # Cliente HTTP y servicios API
│   ├── auth/                # Contexto de autenticación
│   ├── chat/                # Componentes del chat de diagnóstico
│   ├── components/
│   │   └── admin/           # Componentes para panel de administración
│   ├── context/             # Contextos React
│   ├── pages/               # Páginas de la aplicación
│   └── App.tsx               # Componente principal y rutas
├── package.json             # Dependencias Node.js
├── vite.config.ts           # Configuración de Vite
└── README.md                 # Documentación específica del frontend
`

## Características Implementadas

### Fase 1 - Control del médico sobre diagnóstico y tratamiento
- Aprobación, modificación o descarte de fármacos sugeridos por el sistema
- Ajuste de dosis pediátrico por peso (mg/kg)
- Selección de medicamentos bajo guías colombianas
- Filtrado por alergias, embarazo y comorbilidades

### Fase 2 - Exactitud del diagnóstico
- Ponderación IDF y secondary_score por demografía (edad/sexo)
- Motor de data_treatment para limpieza y entrenamiento del catálogo
- Preguntas discriminantes para desambiguar diagnósticos
- Auto-detección de síntomas a partir de signos vitales
- Explicaciones en español sencillo para el paciente (patient_summary)

### Sistema Experto - Alimentación de conocimiento
- Interfaz para super_admin que permite importar conocimiento desde archivos **CSV, Excel (XLSX) o JSON**
- Endpoint POST /api/knowledge/import-file con validación y upsert idempotente
- CRUD completo del catálogo con control de roles
- Normalización estricta (minúsculas, sin diacríticos) para evitar colisiones

## Catálogo de Conocimiento

El sistema cuenta con el siguiente catálogo inicial (seed):

| Colección | Registros | Campos |
|---|---|---|
| symptoms | 276 | 
ame, description, category |
| diseases | 51 | 
ame, description, symptoms, severity |
| 	reatments | 51 | disease_name, medicines, lternative_medicines, 
on_pharmacological_treatments |

## Instalación y Ejecución

### Requisitos Previos
- Python 3.11+ (para backend)
- Node.js 18+ (para frontend)
- Instancia de MongoDB Atlas o MongoDB local

### Backend

`ash
cd backend
pip install -r requirements.txt
uvicorn main:app --port 8001 --reload
`

El backend estará disponible en http://localhost:8001. Swagger UI: http://localhost:8001/docs

### Frontend

`ash
cd frontend
npm install
npm run dev
`

El frontend estará disponible en http://localhost:5173

### Docker

Para ejecutar MongoDB localmente:

`ash
docker-compose up -d
`

## Variables de Entorno

### Backend (.env)
Principales variables de configuración (ver ackend/app/config.py para lista completa):
- MONGODB_URL - Cadena de conexión a MongoDB
- MONGODB_DB_NAME - Nombre de la base de datos
- JWT_SECRET - Clave secreta para JWT
- GEMINI_API_KEY / OPENAI_API_KEY / TOGETHER_API_KEY - Claves para proveedores de IA
- GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET - OAuth de Google
- SMTP_* / GMAIL_API_* / SENDGRID_API_KEY - Configuración de correo
- CORS_ORIGINS - Orígenes permitidos

### Frontend (.env)
- VITE_API_URL - URL del backend (ej.: http://localhost:8001 en desarrollo)

## Endpoints Principales

| Método | Ruta | Descripción |
|---|---|---|
| POST | /api/auth/register | Registro de usuario (con verificación de correo) |
| POST | /api/auth/login | Inicio de sesión |
| POST | /api/auth/verify-email | Verificación de código de 6 dígitos |
| POST | /api/auth/social-login | Inicio de sesión con Google |
| POST | /api/auth/create-user | Creación de usuarios (admin/super_admin) |
| POST | /api/converse | Chat conversacional de diagnóstico |
| POST | /api/diagnose | Diagnóstico por lista de síntomas |
| POST | /api/report | Generación de historia clínica en PDF |
| GET | /api/knowledge/symptoms | Listado de síntomas |
| GET | /api/knowledge/diseases | Listado de enfermedades |
| GET | /api/knowledge/treatments | Listado de tratamientos |
| POST | /api/knowledge/import-file | Importación de catálogo (super_admin) |
| GET | /health | Estado del servicio |

## Pruebas

### Backend
`ash
cd backend
pytest
`

### Frontend
`ash
cd frontend
npm run test
`

## Despliegue

- **Frontend**: Desplegado en Vercel (configurar VITE_API_URL hacia backend)
- **Backend**: Desplegado en Render (usar start_backend.ps1 como comando de inicio)
- **Base de datos**: MongoDB Atlas

## Características de Seguridad

- Autenticación mediante JWT
- Verificación de correo electrónico con código de 6 dígitos (válido por 10 minutos)
- Control de acceso basado en roles (RBAC)
- Autenticación OAuth 2.0 con Google
- Validación estricta de datos con Pydantic
- Logging estructurado con equest_id

## Contribución

Este proyecto fue desarrollado para la Electiva CPC, siguiendo las fases de implementación especificadas para el desarrollo del sistema experto médico.

## Documentación Adicional

- [Documentación Backend](/backend/README.md)
- [Documentación Frontend](/frontend/README.md)
