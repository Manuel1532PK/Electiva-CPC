# Datos de prueba MIMETIC

Datos de demostración para validar el login, el panel del médico y el portal del paciente.
Todo se puede regenerar sin tocar datos reales.

## Cómo sembrar / regenerar

Con MongoDB local encendido y el backend habiendo arrancado al menos una vez
(para que exista la base de conocimiento):

```powershell
cd backend
python seed_demo.py
```

El script es idempotente:

- Crea o actualiza el hospital `DEMO-001`, los usuarios y las 3 historias clínicas.
- Borra **solo** las sesiones marcadas con `demo_seed: true` y las vuelve a crear.
- Genera diagnósticos con el motor experto real, tratamientos y el reporte HTML
  usando el mismo endpoint que la aplicación.

## Credenciales

Contraseña para todas las cuentas: **`Mimetic123!`**

| Rol | Correo | Documento | Nombre |
|-----|--------|-----------|--------|
| Médico | `dra.rios@mimetic.local` | 900123456 | Dra. Valeria Ríos |
| Médico | `medico@mimetic.local` | — | Cuenta existente del proyecto |
| Admin | `admin@mimetic.local` | 900999999 | Admin Demo |
| Paciente | `paciente@mimetic.local` | 1020304050 | Carlos Andrés Mendoza |
| Paciente | `maria@mimetic.local` | 1098765432 | María Fernanda López |
| Paciente | `andres@mimetic.local` | 1000000001 | Andrés Felipe Ramírez |

Hospital de todos: **Hospital Demo MIMETIC** (`DEMO-001`).

## Pacientes y sesiones sembradas

| Paciente | Documento | Sesiones |
|----------|-----------|----------|
| Carlos Andrés Mendoza (39 a) | 1020304050 | Dengue (14/08/2026), Influenza (21/09/2026), Gastroenteritis aguda (19/10/2026) |
| María Fernanda López (31 a) | 1098765432 | Migraña (03/07/2026), Infección urinaria (28/09/2026) |
| Andrés Felipe Ramírez (68 a) | 1000000001 | Infarto agudo de miocardio (11/06/2026), Hipertensión arterial (02/10/2026) |

Cada sesión incluye motivo de consulta, evolución, antecedentes, signos vitales,
síntomas, diagnósticos diferenciales del motor experto, tratamiento y reporte HTML.
Tres sesiones (la más reciente de cada paciente) incluyen además **triaje
Manchester/ESI** y **laboratorio urgente** para probar el panel clínico:

| Paciente | Triaje | SpO₂ | Laboratorio |
|----------|--------|------|-------------|
| Carlos (19/10/2026) | Nivel 3 · Amarillo · NEWS2 = 2 | 96 % | pO₂ 92, lactato 1.8, leucocitos 11.4, creatinina 0.9, PCR 28 |
| María (28/09/2026) | Nivel 3 · Amarillo · NEWS2 = 1 | 97 % | pO₂ 95, lactato 1.2, leucocitos 12.8, creatinina 0.8, PCR 46 |
| Andrés (02/10/2026) | Nivel 3 · ESI · NEWS2 = 3 | 95 % | pO₂ 88, lactato 1.5, leucocitos 8.2, creatinina 1.3, PCR 12 |

## Guion de prueba

### 0. Login

1. Abre `http://127.0.0.1:5173/login`.
2. Entra con `dra.rios@mimetic.local` / `Mimetic123!`.
3. Verifica el estado real de la base de datos y la latencia en el pie del login.
4. El bloque MFA es una **simulación visual**; no se envía ningún código.

### 1. Portal del paciente

1. Entra con `paciente@mimetic.local` / `Mimetic123!`.
2. En **Resumen** verifica: 3 consultas, hospital visitado y última consulta (19/10/2026).
3. En **Historial de Consultas** abre una consulta: síntomas, diagnósticos, tratamiento y reporte.
4. En **Mis Tratamientos** revisa los medicamentos y recomendaciones.
5. Repite con `maria@mimetic.local` (2 sesiones) y `andres@mimetic.local` (2 sesiones, casos críticos).

### 2. Panel del médico

1. Entra con `dra.rios@mimetic.local` / `Mimetic123!`.
2. En **Buscar paciente** escribe `1020304050` (también puedes usar las tarjetas demo).
3. El resultado debe mostrar los badges **Historia Clínica** y **Cuenta Pública**.
4. Al seleccionarlo, el flujo entra en modo **Datos de la sesión** (1/5): los datos
   demográficos vienen precargados desde la historia clínica y el panel izquierdo
   muestra la última sesión como referencia (no se copia al formulario).
5. En el panel izquierdo verifica:
   - **Triaje clínico:** Nivel 3 · Amarillo · Manchester · NEWS2 = 2.
   - **Vitales:** FC 92, SpO₂ 96 %, PA 110/70, FR 18, T 37.9, IMC 25.8.
   - **ECG:** animación simulada a 92 lpm (no hay telemetría real).
   - **Laboratorio:** pO₂ 92, lactato 1.8, leucocitos 11.4, creatinina 0.9, PCR 28.
   - **FHIR R4:** bundle de demostración etiquetado como simulado.
6. Avanza los 5 pasos del formulario, ajusta triaje/laboratorio si quieres y pulsa
   **Finalizar y comenzar consulta**. La nueva sesión se guarda en MongoDB.
7. En el chat escribe los síntomas, usa los comandos `/triaje`, `/lab`, `/fhir`,
   `/listo` o el dictado simulado, confirma un diagnóstico, selecciona medicamentos
   y genera la historia clínica.
8. En la vista del reporte prueba **Imprimir**, **Descargar**, **Abrir**, **Copiar**,
   **Volver al diagnóstico** y **Nueva consulta**.
9. Repite la búsqueda con `1098765432` y `1000000001`.
10. Para probar una consulta completa desde cero, usa **+ Nueva consulta**.

### 3. Historial clínico, vista previa y PDF

El ciclo real del expediente es: **paciente → atenciones → documento → PDF**. No es
una copia del prototipo: la vista previa y el PDF trabajan sobre datos persistidos.

1. En la barra lateral pulsa **Historial clínico**.
2. En **Actividad reciente** aparecen los 3 pacientes con atenciones. También puedes
   buscar por documento (`1020304050`, `1098765432`, `1000000001`).
3. Abre un paciente y revisa la ficha y la línea de tiempo:
   - filtros por **diagnósticos, laboratorio, recetas y documentos**;
   - cada atención muestra vitales, triaje, diagnósticos y documento;
   - las atenciones sin cierre aparecen como **sin documento** y sus botones de
     vista previa/PDF quedan deshabilitados (las 7 sesiones demo sí tienen documento).
4. **Vista previa** en una atención abre el segundo panel con el `report_html`
   guardado en MongoDB, tal como se generó al cerrar la consulta.
5. **PDF** en una atención abre ese mismo documento y lanza el diálogo de impresión.
6. **Vista previa** en el encabezado abre la **historia consolidada** de todas las
   atenciones, generada en el navegador a partir de los datos persistidos.
7. **Descargar PDF** abre la consolidada y lanza el diálogo de impresión: elige
   **Guardar como PDF** en el navegador. No se añadió ninguna dependencia de PDF y
   el archivo no se envía a ningún servidor.
8. Desde el visor también puedes **Imprimir**, descargar **HTML**, **Abrir** en otra
   pestaña o **Copiar** el HTML del documento.
9. **Nueva atención** abre una consulta nueva para ese paciente con identidad y
   última sesión precargadas, sin duplicar la historia clínica.

> **Diseño de los documentos.** Tanto el reporte por atención como la historia
> consolidada usan la misma plantilla print-first: tamaño Letter, masthead MIMETIC,
> tarjeta de paciente, secciones numeradas `01–07`, vitales, triaje, laboratorio,
> receta y pie legal. Los 7 documentos demo ya guardados se regeneraron con
> `backend/regenerate_reports.py`; tras cambiar la plantilla vuelve a ejecutarlo
> para actualizar los `report_html` existentes sin tocar los datos clínicos.

#### FHIR R4 (pestaña separada y simulada)

- La pestaña **FHIR R4 · simulado** muestra un `Bundle` de tipo `collection` armado en
  el navegador: `Patient`, `Encounter`, `Observation`, `Condition`,
  `MedicationRequest` y `DocumentReference`.
- Se puede **descargar JSON**, **copiar** o **ver JSON**. El bundle incluye
  `meta.tag = SIMULATED-DEMO`.
- **No** se valida contra perfiles HL7 ni se envía a HAPI FHIR, SAP/Cerner o un HIS.
  Los códigos LOINC/SNOMED/RxNorm aún no se resuelven: el bundle usa texto libre.
- El bundle **no** forma parte del PDF: el PDF es el documento clínico, no un
  artefacto de interoperabilidad.

### 4. Flujo completo nuevo (opcional)

1. Con la sesión del médico, registra un paciente nuevo y completa anamnesis,
   antecedentes y signos vitales.
2. Describe síntomas en el chat (por ejemplo: fiebre, dolor de cabeza y dolor
   detrás de los ojos).
3. Confirma el diagnóstico, revisa el tratamiento y genera el reporte.
4. Cierra sesión y entra con la cuenta del paciente para ver la nueva consulta.

## Qué es real y qué es simulado

| Función | Estado |
|---------|--------|
| Login, JWT, roles y sesión | Real (backend) |
| Búsqueda de pacientes e historias | Real (MongoDB) |
| Guardado de anamnesis, antecedentes, vitales | Real (MongoDB) |
| Triaje (nivel, sistema, score, discriminadores) | Real: se guarda y se muestra |
| Laboratorio urgente (pO₂, lactato, etc.) | Real: se guarda y se muestra |
| Motor de diagnóstico y tratamientos | Real (motor experto local) |
| Reporte HTML | Real: se genera y ahora incluye SpO₂, triaje y laboratorio |
| Historial clínico persistido | Real: lectura de `clinical_histories` y `sessions` |
| Vista previa y PDF de la historia | Real en el navegador: HTML persistido + diálogo de impresión |
| Bundle FHIR R4 exportable | **Simulado**: mapeo local, sin validación ni envío |
| ECG animado | **Simulado** (sin telemetría) |
| Solicitud de cama | **Simulado** (modal demo) |
| Dictado por voz | **Simulado** (sin captura de audio) |
| MFA / WebAuthn / YubiKey | **Simulado** o roadmap |
| Firma electrónica y envío institucional | Roadmap |

> Los campos de triaje y laboratorio son aditivos: si una sesión antigua no los
> tiene, el panel muestra "—" o una sugerencia NEWS2 calculada con los vitales.

## Limpiar los datos demo

Las sesiones demo están marcadas con `demo_seed: true`. Para eliminarlas sin tocar
datos reales:

```js
// mongosh
db.getSiblingDB("mimetic_ai").sessions.deleteMany({ demo_seed: true })
db.getSiblingDB("mimetic_ai").clinical_histories.deleteMany({ demo_seed: true })
db.getSiblingDB("mimetic_ai").users.deleteMany({
  email: { $in: [
    "dra.rios@mimetic.local",
    "admin@mimetic.local",
    "paciente@mimetic.local",
    "maria@mimetic.local",
    "andres@mimetic.local"
  ]}
})
```

> Nota: el MongoDB que usa el backend es el `mongod` nativo de Windows en
> `127.0.0.1:27017`. El contenedor Docker `mimetic-mongo` puede estar vacío.
