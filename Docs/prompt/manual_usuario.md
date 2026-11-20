# Manual de usuario — MIMETIC AI v1.2

**Versión del documento:** 1.0  
**Fecha:** 2026-11-20  
**Aplicación:** MIMETIC AI — Sistema conversacional de apoyo al diagnóstico médico  
**Público objetivo:** personal clínico, administradores y pacientes  

---

## Índice

1. [Introducción](#1-introducción)
2. [Acceso y requisitos](#2-acceso-y-requisitos)
3. [Roles y permisos](#3-roles-y-permisos)
4. [Primer ingreso](#4-primer-ingreso)
5. [Portal del paciente](#5-portal-del-paciente)
6. [Portal del médico](#6-portal-del-médico)
7. [Panel de administración](#7-panel-de-administración)
8. [Historia clínica y documentos](#8-historia-clínica-y-documentos)
9. [Correo y verificación](#9-correo-y-verificación)
10. [Despliegue y mantenimiento](#10-despliegue-y-mantenimiento)
11. [Limitaciones y funciones simuladas](#11-limitaciones-y-funciones-simuladas)
12. [Preguntas frecuentes](#12-preguntas-frecuentes)
13. [Glosario](#13-glosario)

---

## 1. Introducción

MIMETIC AI es una aplicación web que apoya el trabajo clínico con:

- Un portal para **pacientes**.
- Un portal para **médicos** con un asistente conversacional de diagnóstico.
- Un panel de **administración** para usuarios, hospitales y catálogo clínico.
- Generación de **historia clínica** y documentos en HTML/PDF.
- Integración simulada con estándares **FHIR R4**.

El sistema está pensado como herramienta de apoyo, **no reemplaza el criterio médico**.

### Estado actual

- Frontend en producción: `https://mimetic-ai-v12.vercel.app`
- Backend en producción: `https://mimetic-ai-api-v12.onrender.com`
- Verificación de estado: `https://mimetic-ai-api-v12.onrender.com/health`
- Base de datos: MongoDB Atlas, producción activa y conectada.

---

## 2. Acceso y requisitos

### Requisitos del usuario

- Navegador moderno: Chrome, Edge, Firefox o Safari.
- Conexión a internet.
- Correo electrónico válido para el registro de pacientes.
- Cuenta otorgada por un administrador para médicos y administradores.

### Dirección de acceso

```text
https://mimetic-ai-v12.vercel.app
```

### Idioma

La interfaz está en **español**.

### Tiempo de primera carga

El backend usa un plan gratuito en Render. Si lleva tiempo sin uso, la primera petición puede tardar entre **30 y 60 segundos** mientras el servidor se activa.

---

## 3. Roles y permisos

MIMETIC AI tiene cuatro roles.

| Rol | Qué puede hacer |
|---|---|
| **Paciente** | Ver su historia clínica, consultas, tratamientos y reportes. |
| **Médico** | Buscar pacientes, registrar consultas, usar el asistente de diagnóstico, confirmar diagnósticos, generar historia clínica y documentos. |
| **Administrador** | Crear y ver usuarios de su hospital (médicos y pacientes) y usar el portal clínico. |
| **Superadministrador** | Administrar usuarios de cualquier hospital, hospitales, importar catálogo clínico y usar el portal clínico. |

### Restricciones importantes

- Un paciente solo ve **su propia** información.
- Un administrador de hospital solo puede crear **médicos y pacientes** de su propio hospital.
- Un superadministrador puede crear cualquier tipo de usuario.
- Solo un superadministrador puede importar catálogo clínico.
- Un administrador no puede crear superadministradores.

---

## 4. Primer ingreso

### 4.1 Registro de paciente

1. Abre `https://mimetic-ai-v12.vercel.app`.
2. En la pantalla de inicio de sesión, presiona **“Regístrate”**.
3. Completa el formulario:
   - Nombres y apellidos.
   - Tipo y número de documento.
   - Fecha de nacimiento.
   - Correo electrónico.
   - Teléfono.
   - País, departamento y ciudad.
   - Contraseña.
4. Presiona **“Crear cuenta”**.
5. El sistema enviará un **código de verificación de 6 dígitos** a tu correo.
6. Escribe el código en la pantalla **“Verifica tu correo”**.
7. Si el código es correcto, quedarás autenticado y serás redirigido al portal.

### 4.2 Registro con Google

1. En la pantalla de login, presiona **“Continuar con Google”**.
2. Selecciona tu cuenta de Google.
3. Si es la primera vez, el sistema pedirá confirmar tus datos.
4. Recibirás un código de verificación en tu correo.
5. Escribe el código para completar el registro.

### 4.3 Inicio de sesión

1. Abre la aplicación.
2. Escribe tu correo y contraseña.
3. Presiona **“Ingresar al sistema clínico”**.

El sistema te redirigirá automáticamente según tu rol:

- Paciente → `/paciente`
- Médico → `/chat`
- Administrador o superadministrador → `/admin`

### 4.4 Cierre de sesión

1. En la esquina superior derecha, presiona **“Cerrar sesión”**.
2. El sistema borrará tu token de acceso.

---

## 5. Portal del paciente

### Para qué sirve

El portal del paciente permite consultar tu información médica de forma sencilla y visual.

### Secciones

#### **Resumen**

Muestra:

- Número de consultas realizadas.
- Número de diagnósticos.
- Hospitales visitados.
- Fecha de la última consulta.
- Tu información básica:
  - Nombre.
  - Documento.
  - Fecha de nacimiento.
  - Edad.
  - Género.
  - Teléfono.

#### **Historial de consultas**

Muestra una línea de tiempo con tus atenciones médicas.

Cada consulta incluye:

- Fecha.
- Motivo de consulta.
- Síntomas.
- Diagnósticos y severidad.
- Signos vitales.
- Alergias.
- Tratamiento indicado.

Puedes expandir una consulta para ver más detalles.

#### **Mis tratamientos**

Muestra los medicamentos indicados por cada diagnóstico:

- Medicamento.
- Dosis.
- Frecuencia.
- Duración.
- Vía de administración.
- Recomendaciones en lenguaje claro.

### Acciones disponibles

- Ver resumen.
- Ver historial de consultas.
- Ver tratamientos.
- Ver reporte completo de una consulta.
- Cerrar sesión.

---

## 6. Portal del médico

### Para qué sirve

El portal del médico permite:

- Buscar un paciente por número de documento.
- Crear una nueva consulta.
- Registrar anamnesis, antecedentes, signos vitales, triaje y laboratorio.
- Conversar con el asistente de diagnóstico.
- Confirmar o rechazar diagnósticos.
- Ajustar tratamientos y dosis.
- Generar historia clínica y documentos.

### 6.1 Buscar un paciente

1. En el menú lateral, selecciona **“Búsqueda de paciente”**.
2. Escribe el número de documento.
3. El sistema mostrará los resultados.
4. Selecciona el paciente correcto.

### 6.2 Crear una consulta nueva

1. En la pantalla de búsqueda, presiona **“Nueva consulta”**.
2. El sistema abrirá un formulario con varios pasos.
3. Completa cada sección:
   - Anamnesis.
   - Antecedentes.
   - Signos vitales.
   - Triaje.
   - Laboratorio urgente.
4. Presiona **“Finalizar y comenzar consulta”**.

### 6.3 Consulta clínica conversacional

1. Describe los síntomas del paciente en lenguaje natural.
   - Ejemplo: “Tiene dolor de cabeza y fiebre desde ayer”.
2. El asistente mostrará los síntomas detectados.
3. Puedes usar comandos rápidos:
   - `/triaje`
   - `/lab`
   - `/fhir`
   - `/listo`
4. El asistente mostrará **diagnósticos diferenciales** con:
   - Nombre del diagnóstico.
   - Nivel de confianza.
   - Severidad.
   - Síntomas relacionados.
5. Puedes:
   - Confirmar un diagnóstico.
   - Rechazar un diagnóstico.
   - Agregar un diagnóstico manual.
   - Escribir notas.
6. Cuando escribas el nombre de un diagnóstico confirmado, el asistente mostrará el **tratamiento recomendado**.

### 6.4 Tratamiento

El sistema muestra:

- Medicamentos recomendados.
- Dosis calculada, incluyendo cálculo por peso si aplica.
- Frecuencia.
- Duración.
- Vía.
- Contraindicaciones por alergia, embarazo o comorbilidad.
- Recomendaciones no farmacológicas.

Puedes seleccionar los medicamentos que vas a indicar y ajustar la dosis si es necesario.

### 6.5 Generar historia clínica

1. Asegúrate de tener al menos **un diagnóstico confirmado**.
2. Presiona **“Confirmar y generar historia clínica”**.
3. El sistema generará el documento y lo guardará en la base de datos.
4. Podrás verlo en pantalla, imprimirlo o descargarlo.

---

## 7. Panel de administración

### Para qué sirve

El panel de administración permite gestionar usuarios, hospitales y catálogo clínico.

### 7.1 Usuarios

Puedes:

- Crear usuarios.
- Ver la lista de usuarios.
- Filtrar por rol y hospital.

**Permisos:**

- **Administrador:** puede crear médicos y pacientes de su hospital.
- **Superadministrador:** puede crear cualquier tipo de usuario y elegir el hospital.

### 7.2 Hospitales

Solo disponible para **superadministradores**.

Puedes:

- Crear hospitales.
- Ver la lista de hospitales.
- Activar o desactivar un hospital.
- Eliminar un hospital solo si no tiene usuarios asignados.

### 7.3 Sistema experto

Solo disponible para **superadministradores**.

Permite importar catálogo clínico desde archivos:

- CSV.
- Excel.
- JSON.

Puedes importar:

- Síntomas.
- Enfermedades.
- Tratamientos.

El sistema muestra un resumen con:

- Registros detectados.
- Insertados.
- Actualizados.
- Errores.

---

## 8. Historia clínica y documentos

### 8.1 Historia clínica del paciente

El médico puede consultar:

- Actividad reciente.
- Línea de tiempo de atenciones.
- Diagnósticos.
- Laboratorio.
- Recetas.
- Documentos.

Puede filtrar por:

- Todas las atenciones.
- Diagnósticos.
- Laboratorio.
- Recetas.
- Documentos.

### 8.2 Documento por atención

Cada atención puede tener un **documento HTML** generado al cerrar la consulta.

Acciones disponibles:

- Vista previa.
- Imprimir.
- Descargar HTML.
- Abrir en una pestaña nueva.
- Copiar HTML.
- Descargar PDF usando el diálogo de impresión del navegador.

### 8.3 Historia consolidada

El médico también puede generar un documento con **todas las atenciones** de un paciente.

Acciones:

- Vista previa consolidada.
- Descargar PDF consolidado.
- Descargar HTML.
- Copiar.
- Abrir.

### 8.4 FHIR R4 simulado

El sistema puede generar un **bundle FHIR R4 simulado** con:

- Patient.
- Encounter.
- Observations de signos vitales y laboratorio.
- Conditions.
- MedicationRequests.
- DocumentReference.

Este módulo es **simulado** y no envía datos a un sistema externo.

---

## 9. Correo y verificación

### Cómo funciona

1. Al registrarte, el sistema genera un código de 6 dígitos.
2. El código se envía a tu correo.
3. El código es válido por **10 minutos**.
4. Debes escribirlo en la pantalla de verificación.
5. Si el código es correcto, tu cuenta queda verificada.

### Estado actual

- El correo en producción está configurado con **Gmail API**.
- Si el sistema no puede enviar el correo, responde con un **error 503** en lugar de fingir que lo envió.
- Si estás en modo desarrollo, el sistema puede mostrar el código en pantalla solo si la opción `DEV_EMAIL_FALLBACK` está activada.

---

## 10. Despliegue y mantenimiento

### 10.1 Frontend

- **Plataforma:** Vercel.
- **Proyecto:** `mimetic-ai-v12`.
- **Rama de producción:** `produccion-frontend`.
- **Carpeta raíz:** `Mimetic_V._1.2/frontend`.
- **Comando de build:** `npm ci && npm run build`.
- **Carpeta de salida:** `dist`.

### 10.2 Backend

- **Plataforma:** Render.
- **Servicio:** `mimetic-ai-api-v12`.
- **Rama de producción:** `produccion-backend`.
- **Carpeta raíz:** `Mimetic_V._1.2/backend`.
- **Comando de build:** `pip install -r requirements.txt`.
- **Comando de arranque:** `uvicorn main:app --host 0.0.0.0 --port $PORT`.
- **Health check:** `/health`.

### 10.3 Base de datos

- **Motor:** MongoDB Atlas.
- **Base de datos:** `mimetic_ai`.
- **Estado:** conectada.

### 10.4 Variables de entorno relevantes

Estas variables se configuran en el servidor, no en el código:

- `MONGODB_URL`
- `MONGODB_DB_NAME`
- `JWT_SECRET`
- `CORS_ORIGINS`
- `EMAIL_PROVIDER`
- `FROM_EMAIL`
- `GMAIL_API_CLIENT_ID`
- `GMAIL_API_CLIENT_SECRET`
- `GMAIL_API_REFRESH_TOKEN`

---

## 11. Limitaciones y funciones simuladas

Estas funciones están en la interfaz, pero **no** están conectadas a sistemas reales:

| Función | Estado |
|---|---|
| FHIR R4 | Simulado en el navegador. |
| ECG animado | Simulado. |
| Dictado por voz | Simulado. |
| MFA / WebAuthn / YubiKey | Demo visual. |
| Solicitud de cama | Modal demo. |
| PDF | Se genera con el diálogo de impresión del navegador. |
| Firma electrónica | En roadmap. |
| Envío a HIS | En roadmap. |
| Recuperación de contraseña | No habilitada. Contacta al administrador. |

---

## 12. Preguntas frecuentes

### ¿Qué hago si no recibo el código de verificación?

1. Revisa la carpeta de **spam** o **promociones**.
2. Verifica que escribiste bien tu correo.
3. Si el problema continúa, contacta al administrador.

### ¿Puedo usar MIMETIC AI sin conexión?

No. La aplicación necesita internet para funcionar.

### ¿Un paciente puede ver la información de otro paciente?

No. Cada paciente solo ve su propia información.

### ¿Un administrador puede crear médicos de otro hospital?

No. Un administrador solo puede crear médicos y pacientes de su propio hospital.

### ¿Cómo obtengo una cuenta de médico?

Debes solicitarla a un administrador del hospital.

### ¿Cómo se genera el PDF?

1. Abre el documento.
2. Presiona **“Imprimir”** o **“Descargar PDF”**.
3. En el diálogo del navegador, selecciona **“Guardar como PDF”**.

### ¿Qué hago si la primera carga es lenta?

El backend usa un plan gratuito. Si lleva tiempo sin uso, la primera petición puede tardar entre 30 y 60 segundos.

---

## 13. Glosario

| Término | Significado |
|---|---|
| **JWT** | Token de acceso usado para mantener la sesión iniciada. |
| **RBAC** | Control de acceso por roles. |
| **FHIR R4** | Estándar de interoperabilidad médica. |
| **Triaje** | Clasificación de la urgencia del paciente. |
| **Diagnóstico diferencial** | Posibles diagnósticos según los síntomas. |
| **Historia clínica** | Expediente médico del paciente. |
| **PDF** | Documento portátil generado desde el navegador. |

---

## 14. Recomendaciones finales

- Cierra sesión cuando termines.
- No compartas tu contraseña.
- Usa contraseñas fuertes.
- Verifica que el paciente seleccionado sea el correcto antes de generar documentos.
- Recuerda que el asistente es una **ayuda**, no un reemplazo del criterio médico.
- Si encuentras un error, repórtalo al administrador del sistema.
