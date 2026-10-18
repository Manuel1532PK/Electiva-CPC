# Electiva CPC - Sistema Experto MIMETIC AI

Sistema de apoyo al diagnóstico médico con motor de sistema experto, desarrollado como parte de la Electiva CPC. Este proyecto implementa una arquitectura completa con backend en FastAPI, frontend en React/Vite, base de datos MongoDB Atlas y funcionalidades de diagnóstico conversacional asistido por IA.

## ¿Qué es MIMETIC AI?

MIMETIC AI es un sistema conversacional de apoyo al diagnóstico médico y gestión de flujos que permite a los médicos registrar pacientes, describir síntomas en lenguaje natural y obtener diagnósticos diferenciales con sus respectivos tratamientos. Incluye control del médico sobre diagnósticos y tratamientos, ajuste de dosis por peso/edad/embarazo/alergias y generación de historias clínicas en PDF.

## Contexto y Fase de Análisis (Origen del Proyecto)

El desarrollo de MIMETIC AI nace a partir de una exhaustiva fase de investigación y análisis de las dinámicas hospitalarias actuales, planteado inicialmente como un modelo de "Gemelo Digital" para la gestión integral de pacientes.

### El Problema
Los hospitales, tanto públicos como privados, enfrentan diariamente problemas críticos que afectan directamente la calidad de la atención y la seguridad del paciente. Durante la fase de análisis se identificaron las siguientes problemáticas principales:
*   **Saturación de los servicios de urgencias:** Falta de camillas y demoras que ponen en riesgo la salud de los pacientes.
*   **Cancelación de cirugías:** Derivada de la mala asignación o falta de camas en piso o UCI.
*   **Falta de visibilidad en tiempo real:** Desconocimiento de la disponibilidad exacta de camillas, monitores y personal médico, haciendo ineficiente la asignación de recursos.
*   **Alta carga administrativa:** El personal médico dedica hasta un 30% de su tiempo a registrar información en lugar de atender a los pacientes.

### Objetivos del Análisis Inicial
El análisis se centró en diseñar una solución (basada en IA, IoT y procesamiento de lenguaje natural) capaz de predecir la saturación hospitalaria, optimizar la asignación de recursos y, crucialmente, **apoyar la toma de decisiones clínicas en tiempo real**, lo cual dio paso al desarrollo del actual Sistema Experto de diagnóstico.

### Metodología de Análisis (Fase 1: Análisis y Modelado)
Antes de escribir el código o definir la arquitectura final, el proyecto pasó por una rigurosa fase de análisis cualitativo y cuantitativo:
1.  **Mapeo de procesos:** Se diagramaron los flujos actuales (urgencias, hospitalización, quirófano) mediante el estándar BPMN para consensuar la definición de cuellos de botella.
2.  **Definición de KPIs:** Se identificaron indicadores clave de rendimiento, tales como el tiempo de espera, la ocupación de camas y la tasa de cancelación de cirugías.
3.  **Recolección de necesidades:** Se realizaron entrevistas cualitativas y estructuradas con médicos, enfermeros y gestores hospitalarios para garantizar que la solución de IA (como el chat diagnóstico y la generación automática de historias clínicas) respondiera a necesidades reales y aliviara la carga administrativa.

---

## Tecnologías Utilizadas

| Capa | Tecnologías |
|---|---|
| **Backend** | Python 3.11+, FastAPI, Motor (MongoDB), Pydantic, Uvicorn |
| **Frontend** | React 18.3.1, Vite, TypeScript, React Router DOM, @react-oauth/google |
| **Base de Datos** | MongoDB Atlas (Logs estructurados, eventos, historiales) |
| **IA y Servicios** | Gemini, OpenAI, Together, Gmail API, SMTP, SendGrid, Google OAuth 2.0 |

## Arquitectura del Sistema

```text
Frontend (React + Vite) ──► Backend (FastAPI) ──► MongoDB Atlas
                              │
                              ▼
                Gmail API / SMTP / SendGrid · Gemini / OpenAI / Together
```

## Roles del Sistema

| Rol | Descripción |
|---|---|
| **super_admin** | Acceso completo al sistema. Gestiona usuarios, hospitales y el catálogo de conocimiento (importación de CSV, Excel o JSON). |
| **admin** | Gestiona usuarios y hospitales. |
| **médico** | Utiliza el chat de diagnóstico, gestiona historias clínicas y aprueba, modifica o descarta tratamientos. |
| **paciente** | Consulta sus diagnósticos y tratamientos asignados. |

## Estructura del Proyecto

### Backend (/backend)

```text
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
```

### Frontend (/frontend)

```text
frontend/
├── src/
│   ├── api/                 # Cliente HTTP y servicios API
│   ├── auth/                # Contexto de autenticación
│   ├── chat/                # Componentes del chat de diagnóstico
│   ├── components/
│   │   └── admin/           # Componentes del panel de administración
│   ├── context/             # Contextos React
│   ├── pages/               # Páginas de la aplicación
│   └── App.tsx              # Componente principal y rutas
├── package.json             # Dependencias Node.js
├── vite.config.ts           # Configuración de Vite
└── README.md                # Documentación específica del frontend
```

## Características Principales

### Control del médico sobre diagnóstico y tratamiento
- **Aprobación o rechazo de tratamientos**: El médico puede aprobar, modificar o descartar los fármacos sugeridos.
- **Ajuste de dosis pediátrico**: Cálculo de dosis por peso (mg/kg).
- **Seguridad del tratamiento**: Filtrado por alergias, embarazo y comorbilidades, siguiendo guías colombianas.

### Mayor precisión en el diagnóstico
- **Ponderación inteligente**: Uso de IDF y secondary_score según edad y sexo para ordenar diagnósticos diferenciales.
- **Preguntas discriminantes**: El sistema realiza preguntas específicas cuando hay varios diagnósticos posibles.
- **Detección automática de síntomas**: Identifica síntomas a partir de signos vitales (fiebre, taquipnea, presión arterial, entre otros).
- **Explicaciones para el paciente**: Genera resúmenes comprensibles (patient_summary) para mejorar la comunicación.

### Sistema Experto - Alimentación del Conocimiento
- **Importación flexible**: Permite importar el catálogo desde archivos CSV, Excel (XLSX) o JSON (solo para super_admin).
- **Actualización inteligente**: Realiza upsert idempotente para evitar duplicados.
- **Normalización estricta**: Convierte a minúsculas y elimina diacríticos para evitar colisiones (ej. "Vómito" y "vomito").
- **CRUD completo**: Gestión del catálogo con control de permisos por rol.

## Catálogo de Conocimiento

| Colección | Registros | Campos |
|---|---|---|
| **symptoms** | 276 | name, description, category |
| **diseases** | 51 | name, description, symptoms, severity |
| **treatments** | 51 | disease_name, medicines, alternative_medicines, non_pharmacological_treatments |

### Requisitos Previos
- [Python 3.11+](https://www.python.org/)
- [Node.js 18+](https://nodejs.org/)
- [MongoDB Atlas](https://www.mongodb.com/atlas) o MongoDB local

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

## Seguridad

- **Autenticación JWT**: Tokens seguros para sesiones.
- **Verificación por correo**: Código de 6 dígitos válido por 10 minutos.
- **RBAC**: Control de acceso basado en roles (super_admin, admin, médico, paciente).
- **OAuth 2.0**: Inicio de sesión con Google.
- **Validación de datos**: Mediante modelos Pydantic.
- **Logging estructurado**: Con request_id para trazabilidad.