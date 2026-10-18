# Electiva CPC - Sistema Experto MIMETIC AI

Sistema de apoyo al diagnóstico médico con motor de sistema experto, desarrollado como parte de la Electiva CPC. Este proyecto implementa una arquitectura completa con backend en FastAPI, frontend en React/Vite, base de datos MongoDB Atlas y funcionalidades de diagnóstico conversacional asistido por IA.

## ¿Qué es MIMETIC AI?

MIMETIC AI es un sistema conversacional de apoyo al diagnóstico médico que permite a los médicos registrar pacientes, describir síntomas en lenguaje natural y obtener diagnósticos diferenciales con sus respectivos tratamientos. Incluye control del médico sobre diagnósticos y tratamientos, ajuste de dosis por peso/edad/embarazo/alergias y generación de historias clínicas en PDF.

## Tecnologías Utilizadas

| Capa | Tecnologías |
|---|---|
| **Backend** | Python 3.11+, FastAPI, Motor (MongoDB), Pydantic, Uvicorn |
| **Frontend** | React 18.3.1, Vite, TypeScript, React Router DOM, @react-oauth/google |
| **Base de Datos** | MongoDB Atlas |
| **IA y Servicios** | Gemini, OpenAI, Together, Gmail API, SMTP, SendGrid, Google OAuth 2.0 |

## Arquitectura del Sistema

`	ext
Frontend (React + Vite) ──► Backend (FastAPI) ──► MongoDB Atlas
                              │
                              ▼
                Gmail API / SMTP / SendGrid · Gemini / OpenAI / Together
`

## Roles del Sistema

| Rol | Descripción |
|---|---|
| **super_admin** | Acceso completo al sistema. Gestiona usuarios, hospitales y el catálogo de conocimiento (importación de CSV, Excel o JSON). |
| **admin** | Gestiona usuarios y hospitales. |
| **médico** | Utiliza el chat de diagnóstico, gestiona historias clínicas y aprueba, modifica o descarta tratamientos. |
| **paciente** | Consulta sus diagnósticos y tratamientos asignados. |

## Estructura del Proyecto

### Backend (/backend)

`	ext
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
├── main.py                  # Punto de entrada de FastAPI
├── seed_data.py             # Datos iniciales del catálogo
├── requirements.txt         # Dependencias Python
└── README.md                # Documentación específica del backend
`

### Frontend (/frontend)

`	ext
frontend/
├── src/
│   ├── api/                 # Cliente HTTP y servicios API
│   ├── auth/                # Contexto de autenticación
│   ├── chat/                # Componentes del chat de diagnóstico
│   ├── components/
│   │   └── admin/           # Componentes del panel de administración
│   ├── context/             # Contextos React
│   ├── pages/               # Páginas de la aplicación
│   └── App.tsx               # Componente principal y rutas
├── package.json             # Dependencias Node.js
├── vite.config.ts           # Configuración de Vite
└── README.md                # Documentación específica del frontend
`

## Características Principales

### Fase 1 - Control del médico sobre diagnóstico y tratamiento
- **Aprobación o rechazo de tratamientos**: El médico puede aprobar, modificar o descartar los fármacos sugeridos.
- **Ajuste de dosis pediátrico**: Cálculo de dosis por peso (mg/kg).
- **Seguridad del tratamiento**: Filtrado por alergias, embarazo y comorbilidades, siguiendo guías colombianas.

### Fase 2 - Mayor precisión en el diagnóstico
- **Ponderación inteligente**: Uso de IDF y secondary_score según edad y sexo para ordenar diagnósticos diferenciales.
- **Preguntas discriminantes**: El sistema realiza preguntas específicas cuando hay varios diagnósticos posibles.
- **Detección automática de síntomas**: Identifica síntomas a partir de signos vitales (fiebre, taquipnea, presión arterial, entre otros).
- **Explicaciones para el paciente**: Genera resúmenes comprensibles (patient_summary).

### Sistema Experto - Alimentación del Conocimiento
- **Importación flexible**: Permite importar el catálogo desde archivos CSV, Excel (XLSX) o JSON (solo para super_admin).
- **Actualización inteligente**: Realiza upsert idempotente para evitar duplicados.
- **Normalización estricta**: Convierte a minúsculas y elimina diacríticos para evitar colisiones (ej. "Vómito" y "vomito").
- **CRUD completo**: Gestión del catálogo con control de permisos por rol.

## Catálogo de Conocimiento

| Colección | Registros | Campos |
|---|---|---|
| **symptoms** | 276 | 
ame, description, category |
| **diseases** | 51 | 
ame, description, symptoms, severity |
| **treatments** | 51 | disease_name, medicines, lternative_medicines, 
on_pharmacological_treatments |

## Instalación y Ejecución

### Requisitos Previos
- [Python 3.11+](https://www.python.org/)
- [Node.js 18+](https://nodejs.org/)
- [MongoDB Atlas](https://www.mongodb.com/atlas) o MongoDB local

### 1. Clonar el repositorio

`ash
git clone https://github.com/Manuel1532PK/Electiva-CPC.git
cd Electiva-CPC
`

### 2. Configurar el Backend

`ash
cd backend
pip install -r requirements.txt
`

Crear un archivo .env con las variables de entorno necesarias (ver sección "Variables de Entorno"). Luego ejecutar:

`ash
uvicorn main:app --port 8001 --reload
`

El backend estará disponible en [http://localhost:8001](http://localhost:8001). Documentación Swagger en [http://localhost:8001/docs](http://localhost:8001/docs).

### 3. Configurar el Frontend

`ash
cd frontend
npm install
npm run dev
`

El frontend estará disponible en [http://localhost:5173](http://localhost:5173).

### 4. MongoDB con Docker (opcional)

`ash
docker-compose up -d
`

## Variables de Entorno

### Backend (ackend/.env)

Las principales variables de configuración son:

| Variable | Descripción | Requerida |
|---|---|---|
| MONGODB_URL | Cadena de conexión a MongoDB Atlas o MongoDB local | Sí |
| MONGODB_DB_NAME | Nombre de la base de datos | No (por defecto: mimetic_ai) |
| JWT_SECRET | Clave secreta para tokens JWT | Sí |
| JWT_ALGORITHM | Algoritmo JWT | No (por defecto: HS256) |
| JWT_EXPIRATION_HOURS | Duración del token en horas | No (por defecto: 24) |
| GEMINI_API_KEY | Clave API para Google Gemini | Recomendado |
| OPENAI_API_KEY | Clave API para OpenAI | Opcional |
| TOGETHER_API_KEY | Clave API para Together | Opcional |
| GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET | Para autenticación con Google OAuth | Opcional |
| GMAIL_API_CLIENT_ID / GMAIL_API_CLIENT_SECRET / GMAIL_API_REFRESH_TOKEN | Para envío de correos con Gmail API | Opcional |
| SMTP_HOST / SMTP_USER / SMTP_PASSWORD | Para envío de correos por SMTP | Opcional |
| SENDGRID_API_KEY | Para envío de correos con SendGrid | Opcional |
| CORS_ORIGINS | Orígenes permitidos (separados por coma) | Opcional |
| LOG_LEVEL | Nivel de logging | No (por defecto: INFO) |

> Para más detalles, consultar ackend/app/config.py.

### Frontend (rontend/.env)

| Variable | Descripción |
|---|---|
| VITE_API_URL | URL del backend. En desarrollo: http://localhost:8001 |

## Endpoints Principales

| Método | Ruta | Descripción |
|---|---|---|
| POST | /api/auth/register | Registro de usuario con verificación por correo electrónico |
| POST | /api/auth/login | Inicio de sesión |
| POST | /api/auth/verify-email | Verificación de código de 6 dígitos |
| POST | /api/auth/social-login | Inicio de sesión con Google |
| POST | /api/auth/create-user | Creación de usuario (admin/super_admin) |
| GET | /api/auth/me | Obtener perfil del usuario autenticado |
| POST | /api/converse | Chat conversacional de diagnóstico |
| POST | /api/diagnose | Diagnóstico por lista de síntomas |
| POST | /api/report | Generar historia clínica en PDF |
| GET | /api/knowledge/symptoms | Listar síntomas |
| GET | /api/knowledge/diseases | Listar enfermedades |
| GET | /api/knowledge/treatments | Listar tratamientos |
| POST | /api/knowledge/import-file | Importar catálogo (solo super_admin) |
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

- **Frontend**: [Vercel](https://vercel.com/) - Configurar VITE_API_URL apuntando al backend. Comando de build: 
pm run build. Directorio de salida: dist.
- **Backend**: [Render](https://render.com/) - Usar start_backend.ps1 como comando de inicio.
- **Base de datos**: [MongoDB Atlas](https://www.mongodb.com/atlas).

## Seguridad

- **Autenticación JWT**: Tokens seguros para sesiones.
- **Verificación por correo**: Código de 6 dígitos válido por 10 minutos.
- **RBAC**: Control de acceso basado en roles (super_admin, admin, médico, paciente).
- **OAuth 2.0**: Inicio de sesión con Google.
- **Validación de datos**: Mediante modelos Pydantic.
- **Logging estructurado**: Con equest_id para trazabilidad.

## Documentación Adicional

- [Documentación del Backend](/backend/README.md)
- [Documentación del Frontend](/frontend/README.md)

## Créditos

Desarrollado como parte de la **Electiva CPC**.