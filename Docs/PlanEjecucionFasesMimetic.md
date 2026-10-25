# Plan de Ejecución por Fases — MIMETIC IA (Prototipo MVP)

---

## 1. Estrategia de entrega

El diseño original de MIMETIC abarca un ecosistema complejo (IoT, Inteligencia Artificial, Blockchain, FHIR R4). Para garantizar una entrega funcional se adopta una estrategia de **Producto Mínimo Viable (MVP)** dividida en fases. El diseño está hecho en **Stitch** y se construirá con un **MCP**.

> **Regla de oro:** cualquier característica, botón o pantalla que no esté explícitamente detallada en el alcance de la **Fase 1** debe ser **ocultada, deshabilitada (estado *disabled* o *mock*) o pospuesta**.

### 1.1 Resumen de fases

| Fase | Nombre | Duración | Semanas |
|------|--------|----------|---------|
| 0 | Preparación, arquitectura y fundaciones | 3 sem | 1–3 |
| 1 | Demo funcional: Identidad, Gestión de usuarios/hospitales e IA Clínica por texto (MVP) | 6 sem | 4–9 |
| 2 | Sistema IoT y rastreo físico | 6 sem | 10–15 |
| 3 | Historia clínica estructurada (HL7/FHIR) y ciclo documental | 5 sem | 16–20 |
| 4 | Salud predictiva, wearables y simulación | 5 sem | 21–25 |
| 5 | Blockchain e integridad documental | 4 sem | 26–29 |
| 6 | Portal del paciente, Hardening y Go-Live | 4 sem | 30–33 |

---

## 2. Arquitectura de referencia

Componentes mencionados en los documentos, y la fase en que se activa cada uno.

| Componente | Descripción según documentos | Fase de activación |
|-----------|------------------------------|--------------------|
| **Base de datos relacional** | PostgreSQL: usuarios, roles, hospitales; más adelante historias clínicas HL7/FHIR | 0 (modelo), 1 (uso), 3 (FHIR) |
| **Base de datos documental** | MongoDB: logs de IA, reportes y registro histórico de eventos IoT (RF03) | 0 (modelo), 1 (logs IA), 2 (eventos IoT) |
| **Librería de componentes UI** | Design system con tokens importados de Stitch (colores, tipografía, radios, sombras) | 0 |
| **Autenticación y RBAC** | Login multi-rol validado contra la base de datos propia (RF13) | 1 |
| **IA clínica** | IA funcional desarrollada por el equipo, por texto, con triaje colombiano (Ley 1751) (RF15) | 1 |
| **Ingesta IoT** | RFID/BLE/peso, simulados o reales; scripts simuladores de telemetría como respaldo | 2 |
| **Nodos edge** | Modo contingencia offline | 2 |
| **HL7/FHIR** | Historia clínica interoperable, bundles, PDF | 3 |
| **Modelos predictivos y wearables** | Redes neuronales para saturación de urgencias; SpO2 y FC post-alta | 4 |
| **Blockchain permisionada** | Ledger, firma electrónica (FIPS) y hash documental | 5 |
| **Portal del paciente** | Resumen en lenguaje sencillo | 6 |

### 2.1 Vista por capas (Fase 1)

```
┌──────────────────────────────────────────────────────────────┐
│ Frontend (componentes basados en tokens de Stitch)           │
│  Login multi-rol │ Médico │ Administrador │ Ingeniero IA     │
├──────────────────────────────────────────────────────────────┤
│ Backend: autenticación + RBAC + gestión de usuarios/hospitales│
│          Integración con la IA clínica (texto, Ley 1751)     │
├───────────────────────────┬──────────────────────────────────┤
│ PostgreSQL                │ MongoDB                          │
│ usuarios, roles,          │ logs de IA                       │
│ hospitales                │                                  │
└───────────────────────────┴──────────────────────────────────┘
   Sin IoT · Sin biometría · Sin integraciones externas · Sin voz
```

### 2.2 Identidad visual
- Color institucional del sidebar: **Teal `#0F766E`**.
- Los tokens del diseño provienen de Stitch y se importan en la Fase 0.

---

## FASE 0 — Preparación, arquitectura y fundaciones

- **Duración:** 3 semanas (Semanas 1–3)
- **Objetivo:** establecer la base técnica y organizativa para la demo funcional: repositorios, base de datos y entornos para la integración de la IA.

### Actividades
1. Constitución del equipo, roles y canales de comunicación.
2. Setup de repositorios, branching strategy y convenciones.
3. Despliegue de entorno de desarrollo y pruebas.
4. Diseño del modelo de datos inicial (PostgreSQL + MongoDB) enfocado en usuarios, roles, logs de IA y reportes.
5. Design system: importación de tokens de Stitch (colores, tipografía, radios, sombras) a la librería de componentes web.
6. Backlog priorizado centrado exclusivamente en el alcance del MVP (Fase 1).

### Entregables
- Repositorios operativos.
- Base de datos inicial estructurada.
- Librería de componentes UI base.
- Backlog priorizado del MVP.

| Pantallas Stitch | RF/RNF |
|------------------|--------|
| Ninguna (fundación de diseño y backend) | RNF16 (Mantenibilidad) |

### Criterios de salida
- Entornos accesibles por todo el equipo.
- Modelo de datos aprobado para soportar flujos de usuarios, IA y reportes.

### Riesgos
- Retrasos en la configuración inicial del entorno de desarrollo.

---

## FASE 1 — Prototipo funcional de gestión y asistencia IA (MVP)

- **Duración:** 6 semanas (Semanas 4–9)
- **Objetivo:** demostrar el núcleo de gestión de usuarios (Hospitales, Administradores, Médicos) y la viabilidad del Asistente Clínico IA con los estándares de triaje de la Ley 1751 de Colombia, de extremo a extremo y sin dependencias de hardware.

### 1.1 Limitaciones generales (lo que NO se hará)
- **Cero hardware / IoT:** sin telemetría, sin conexión a sensores RFID/BLE, sin seguimiento en tiempo real de camas, camillas o quirófanos.
- **Cero biometría real:** sin pulsos cardíacos, sin muestras de SpO2, sin wearables. Todo dato vital en UI es estático (mockup).
- **Cero integración externa:** sin conexión a sistemas HIS/EHR reales ni a bases de datos climáticas.
- Sin transcripción de voz a texto (Whisper/PLN).
- Sin PDFs oficiales ni validaciones Blockchain.

### 1.2 Alcance por rol

#### A. Portal de acceso multi-rol
- **Pantallas:** `SCREEN_65`, `SCREEN_12`, `SCREEN_14` (`mimetic_inicio_de_sesi_n_multi_rol`)
- **En alcance:** login funcional con selector de 3 roles: Médico, Administrador, Ingeniero IA / Super Admin.
- **Limitación:** credenciales validadas contra la base de datos propia; sin verificaciones de hardware FIPS ni RFID.

#### B. Rol Médico asistencial
- **Pantallas:** `SCREEN_61`, `SCREEN_44` (`mimetic_asistente_ia_cl_nico`, `mimetic_historial_cl_nico_del_paciente`)
- **En alcance:**
  1. **Sidebar** siguiendo el diseño institucional (Teal `#0F766E`), con las pestañas de navegación: Asistente IA clínico e Historial médico del paciente.
  2. **Historial médico (`SCREEN_44`):** interfaz del historial del paciente y sus pestañas, con datos estáticos/simulados.
  3. **Asistente IA clínico (`SCREEN_61`) — funcionalidad core:** integrar la IA funcional que ya desarrolló el equipo; interacción por texto, apoyo al diagnóstico y aplicación de las reglas del triaje colombiano (Ley 1751). Los logs de IA se registran en MongoDB.
- **Limitaciones:**
  - Sin voz a texto.
  - Solicitud digital de recursos (`SCREEN_50`) y monitoreo de camas (`SCREEN_48`): solo lectura con datos de prueba, o deshabilitadas.
  - Sin PDFs oficiales ni Blockchain.

#### C. Rol Administrador hospitalario
- **Pantallas:** `SCREEN_8`, `SCREEN_6`, `SCREEN_4`, `SCREEN_2` (`mimetic_asistente_paso_a_paso_alta_de_personal_m_dico`)
- **En alcance:** únicamente la **creación de usuarios médicos**, como demo funcional:
  - Wizard de registro de personal clínico.
  - Formularios para seleccionar rol asistencial, especialidad y permisos.
  - Generación de la credencial digital (simulada) en la base de datos.
- **Limitaciones:**
  - "Panel General y Métricas" (dashboards de saturación) y "Auditoría Blockchain": no funcionales.
  - Panel de "Ocupación de Recursos IoT" (`SCREEN_38`): excluido.

#### D. Rol Ingeniero IA / Super Administrador
- **Pantallas:** `SCREEN_40`, `SCREEN_20`, `SCREEN_32`, `SCREEN_30`, `SCREEN_28` (`mimetic_super_admin_registro_*`)
- **En alcance:**
  1. **Red de hospitales:** alta (creación) funcional de nuevas sedes hospitalarias.
  2. **Gestión de accesos:** wizard funcional para registrar y habilitar Administradores Hospitalarios, asignándolos a un hospital creado previamente.
- **Limitaciones:**
  - Monitorización del clúster GPU y latencia de inferencia Edge: solo visual (diseño estático).
  - Selección de planes SaaS y configuración de Nodos Edge: no aprovisionan infraestructura real.

### 1.3 Cadena de creación en cascada

```
Ingeniero IA ──crea──▶ Hospital ──asigna──▶ Administrador Hospitalario ──crea──▶ Médico ──usa──▶ Asistente IA (texto, Ley 1751)
```

### 1.4 Plan de trabajo sugerido (6 semanas)

| Semana | Foco | Entregable intermedio |
|--------|------|-----------------------|
| 4 | Login multi-rol y RBAC (3 roles) | Login validando contra BD propia |
| 5 | Ingeniero IA: alta de hospitales | Hospital persistido en PostgreSQL |
| 6 | Ingeniero IA: wizard de administradores asignados a hospital | Hospital → Admin operativo |
| 7 | Administrador: wizard de médicos y credencial simulada | Hospital → Admin → Médico operativo |
| 8 | Médico: sidebar, historial (mock) e integración de la IA por texto con triaje Ley 1751 | Asistente IA respondiendo en UI |
| 9 | Ocultar/deshabilitar lo que no es Fase 1, pruebas de extremo a extremo y demo | MVP demostrable |

*(La distribución semanal es una propuesta de organización; los documentos fijan solo la duración total de 6 semanas.)*

### 1.5 Entregables
MVP funcional de software, demostrable de extremo a extremo y sin dependencias de hardware.

### 1.6 RF/RNF e historias de usuario
- **RF:** RF13 (RBAC), RF15 (Diagnóstico IA), RF28 (Gestión de usuarios).
- **HU:** HU-MIMETIC-001, HU-MIMETIC-002 (parcial).

### 1.7 Criterios de salida
- Login y RBAC validan correctamente los 3 roles.
- Creación exitosa de un Hospital → Admin → Médico en base de datos.
- La IA responde aplicando criterios de triaje Ley 1751 vía texto.
- Todo elemento fuera de alcance está oculto, deshabilitado o en modo mock.

### 1.8 Riesgos
- Integración de la IA existente con la interfaz del Asistente Clínico (mitigación: la IA ya es funcional; acotar la integración a texto).

---

## 3. Elementos del plan original diferidos fuera de Fase 1

El plan de ejecución original incluía en la Fase 1 elementos que **contradicen los lineamientos actuales** (Regla de oro y limitaciones de la Fase 1). Se retiran de la Fase 1:

| Elemento | Referencia original | Motivo del retiro | Estado |
|----------|--------------------|--------------------|--------|
| Dictado por voz (speech-to-text, Whisper API) | RF06, RNF02 | La Fase 1 excluye voz a texto | Diferido; **fase por confirmar** |
| Panel de reportes gerenciales con datos sintéticos | RF25 | Dashboards del Administrador no funcionales en Fase 1 | Diferido; **fase por confirmar** |
| Configuración dinámica de parámetros y umbrales | RF27 | Fuera del alcance listado en Fase 1 | Diferido; **fase por confirmar** |
| Gestión del conocimiento (carga de reglas del sistema, configuración base de IA) | Fase 1 original | No figura en el alcance del Ingeniero IA de Fase 1 | Diferido; **fase por confirmar** |
| HU-MIMETIC-010 y HU-MIMETIC-011 | Fase 1 original | Los documentos no detallan su contenido | **Por validar** |

> Los documentos no asignan estos elementos a otra fase. Deben decidirse con el equipo antes del inicio de la Fase 1; este plan no los asigna por su cuenta.

---

## FASE 2 — Implementación del sistema IoT y rastreo físico

- **Duración:** 6 semanas (Semanas 10–15)
- **Objetivo:** dotar al gemelo digital de percepción física: capturar, almacenar y visualizar en tiempo real el estado del hospital mediante IoT, para el rastreo de camas, camillas y quirófanos.

### Actividades
1. Ingesta de eventos IoT (RFID/BLE/peso), simulados o reales.
2. Panel de visibilidad hospitalaria (dashboard) con visualización por pabellón en tiempo real.
3. Solicitud digital de recursos vinculada a los estados de las camas IoT.
4. Modo contingencia offline en nodos edge.
5. Monitorización de estados (Libre, Ocupado, En Limpieza) reflejados en los mapas visuales (`SCREEN_38`, `SCREEN_55`).
6. Configuración de MongoDB para el registro histórico de eventos IoT (RF03).

### Entregables
Módulo IoT operativo y visualización de recursos en los mapas del sistema.

| Pantallas Stitch | RF/RNF | HU |
|------------------|--------|----|
| `mimetic_ocupaci_n_de_camas_iot_y_pabellones`, `mimetic_solicitud_digital_de_recursos_camas_iot_1/2` (`SCREEN_38`, `SCREEN_55`; vistas `SCREEN_48`, `SCREEN_50` pasan de solo lectura a funcionales) | RF01, RF02, RF03, RF04, RF23, RNF01 | HU-MIMETIC-003, HU-MIMETIC-012 |

### Criterios de salida
Un cambio de estado físico (ej. cama ocupada) se refleja en la interfaz en **< 2 s**.

### Limitaciones y riesgos
- Si no se dispone de hardware (gateways BLE/RFID) a escala industrial, se usan simuladores de telemetría (scripts que inyectan datos a la base de datos).
- No se requiere certificación médica de los sensores para el prototipo.
- Riesgo: latencia en la conexión de hardware; mitigación: scripts simuladores de respaldo.

---

## FASE 3 — Historia clínica estructurada (HL7/FHIR) y ciclo documental

- **Duración:** 5 semanas (Semanas 16–20)
- **Objetivo:** almacenar, buscar y exportar historias clínicas bajo estándar HL7/FHIR en PostgreSQL, habilitando la trazabilidad.

### Actividades
1. Adaptación del modelo de datos a estándar HL7/FHIR.
2. Búsqueda por documento, nombre y fechas (< 3 s).
3. Generación de historia en PDF.
4. Trazabilidad clínica y bundles interoperables.

### Entregables
Historial médico estructurado e interoperable.

| Pantallas Stitch | RF/RNF | HU |
|------------------|--------|----|
| `mimetic_historial_cl_nico_del_paciente` (pasa de datos simulados a datos reales) | RF08, RF09, RF12, RF16, RNF11 | HU-MIMETIC-008 |

### Criterios de salida
Generación de PDF y búsqueda sobre dataset de prueba en **< 3 s**.

---

## FASE 4 — Salud predictiva, wearables y simulación

- **Duración:** 5 semanas (Semanas 21–25)
- **Objetivo:** implementar modelos predictivos (redes neuronales) para saturación de urgencias, telemetría de biometría (wearables) y simulador masivo.

### Actividades
1. Ingesta de datos de wearables (SpO2, FC post-alta).
2. Modelo predictivo de saturación de urgencias (≥ 4 h de anticipación).
3. Integración climática y clasificación de hábitos.
4. Simulador de contingencia/eventos masivos.

### Entregables
Módulo predictivo y telemetría de wearables operando.

| RF/RNF | HU |
|--------|----|
| RF17, RF18, RF19, RF20, RF22, RNF03 | HU-MIMETIC-004, HU-MIMETIC-006, HU-MIMETIC-009 |

### Criterios de salida
Precisión del modelo predictivo **≥ 85 %**.

---

## FASE 5 — Blockchain e integridad documental

- **Duración:** 4 semanas (Semanas 26–29)
- **Objetivo:** incorporar inmutabilidad y auditoría criptográfica avanzada (firma FIPS y Ledger).

### Actividades
1. Implementación de red blockchain permisionada.
2. Estampado de firma electrónica y hash documental.
3. Verificación de integridad documental en tiempo real.

### Entregables
Sistema inmutable y auditable legalmente.

| RF/RNF | HU |
|--------|----|
| RF11, RF14, RF24, RNF13 | HU-MIMETIC-007 |

---

## FASE 6 — Portal del paciente, Hardening y Go-Live

- **Duración:** 4 semanas (Semanas 30–33)
- **Objetivo:** cierre del ciclo con la entrega de información al paciente, pruebas finales de seguridad, rendimiento y despliegue.

### Actividades
1. Desarrollo del Portal del Paciente (resumen en lenguaje sencillo).
2. Pruebas de pentesting, carga y rendimiento.
3. Despliegue de la versión completa a producción.

### Entregables
Versión final desplegada (V1.0) con acceso a pacientes.

| RF/RNF | HU |
|--------|----|
| RF10, RF26 | HU-MIMETIC-005 |

---

## 4. Matriz de alcance por fase (qué se activa y cuándo)

| Capacidad | F0 | F1 | F2 | F3 | F4 | F5 | F6 |
|-----------|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| Modelo de datos, repos, design system | ● | | | | | | |
| Login multi-rol y RBAC | | ● | | | | | |
| Alta de hospitales y administradores (Ingeniero IA) | | ● | | | | | |
| Alta de médicos (Administrador) | | ● | | | | | |
| Asistente IA clínico por texto (Ley 1751) | | ● | | | | | |
| Historial del paciente (datos simulados) | | ● | | | | | |
| IoT: camas, camillas, quirófanos | | | ● | | | | |
| Solicitud digital de recursos funcional | | | ● | | | | |
| HL7/FHIR, búsqueda, PDF | | | | ● | | | |
| Wearables, modelo predictivo, simulador | | | | | ● | | |
| Blockchain, firma, hash | | | | | | ● | |
| Portal del paciente, pentesting, Go-Live | | | | | | | ● |
| Voz, reportes, configuración dinámica, gestión del conocimiento | | *diferido — fase por confirmar* | | | | | |

● = se construye en esa fase.

---

