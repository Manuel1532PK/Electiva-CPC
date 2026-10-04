# Requerimientos y Historias de Usuario - Sistema MIMETIC

Este documento consolida los Requerimientos Funcionales (RF), Requerimientos No Funcionales (RNF) y las Historias de Usuario (HU) derivadas de las entrevistas para el sistema MIMETIC.

---

## 1. Requerimientos Funcionales (RF)

| ID | Prioridad | Requerimiento | Descripción | Caso de Uso |
| :--- | :--- | :--- | :--- | :--- |
| **RF01** | Alta | Monitoreo IoT en tiempo real | El sistema debe capturar e integrar en tiempo real el estado y la ubicación de camas, camillas y quirófanos mediante sensores (RFID/BLE/peso), reflejando estados: ocupado, libre, en limpieza y en mantenimiento. | CU-03, CU-04 |
| **RF02** | Alta | Panel de visibilidad hospitalaria (Dashboard) | Ofrecer un panel en tiempo real con ocupación por servicio, camillas libres, pacientes en observación prolongada, tiempos de espera, cancelaciones y ocupación de UCI, refrescándose cada 5 a 10 segundos. | CU-03, CU-05 |
| **RF03** | Alta | Ingesta de eventos IoT y almacenamiento | Almacenar eventos IoT no estructurados y logs en una base de datos MongoDB, conservando el histórico. | CU-04 |
| **RF04** | Alta | Solicitud digital de camillas/quirófanos | Digitalizar el flujo de triaje: el médico solicita recursos desde su módulo y llega automáticamente a Admisiones sin papel. | CU-19, CU-20 |
| **RF05** | Alta | Vinculación de solicitudes a historia clínica | Cada solicitud debe quedar vinculada automáticamente a la historia clínica en menos de 2 segundos. | CU-19 |
| **RF06** | Alta | Transcripción de notas médicas por voz (PLN) | Permitir redactar notas, órdenes y fórmulas mediante comandos de voz en un borrador estructurado editable. | CU-14 |
| **RF07** | Alta | Validación clínica de transcripción | Aplicar diccionario médico, validar términos/dosis contra rangos y solicitar confirmación si la dosis es inusual antes de guardar. | CU-14, CU-15 |
| **RF08** | Alta | Historia clínica estructurada (HL7/FHIR) | Almacenar historias clínicas estructuradas en PostgreSQL bajo el estándar HL7/FHIR garantizando 0 errores de formato. | CU-16 |
| **RF09** | Alta | Búsqueda de historias y resúmenes | Permitir buscar historias y resúmenes por documento, nombre, fechas, servicio o diagnóstico en segundos. | CU-17 |
| **RF10** | Alta | Resumen de atención al alta | Generar y enviar automáticamente el resumen de atención en lenguaje sencillo al paciente (correo/app) con registro de entrega. | CU-23, CU-24 |
| **RF11** | Alta | Registro inmutable (Blockchain) | Registrar inmutablemente cada transacción, consentimiento y orden en Blockchain para verificar que no fue alterado. | CU-21, CU-22 |
| **RF12** | Alta | Trazabilidad de cambios y auditoría | Conservar historial de cambios: quién, cuándo, qué se modificó y rol. | CU-18 |
| **RF13** | Alta | Autenticación, roles y permisos (RBAC) | Gestionar usuarios/roles con JWT/OAuth y validar acceso a funciones correspondientes. | CU-01, CU-02 |
| **RF14** | Alta | Firma electrónica de documentos | Asociar a documentos críticos una firma electrónica con identidad, fecha y vínculo al documento (validez jurídica). | CU-20 |
| **RF15** | Alta | Diagnóstico conversacional asistido | Permitir describir síntomas libremente y sugerir diagnósticos diferenciales, hacer preguntas y recomendar tratamiento ajustado. | CU-27 |
| **RF16** | Alta | Generación de historia clínica en PDF | Generar historia en PDF listo para imprimir/enviar con datos, síntomas, diagnóstico, tratamiento y recomendaciones. | CU-16 |
| **RF17** | Media | Wearables: captura de datos | Recibir y procesar datos de wearables (frecuencia cardíaca, actividad) de pacientes dados de alta. | CU-08, CU-09 |
| **RF18** | Media | Clasificación cualitativa de hábitos | Transformar métricas numéricas en etiquetas cualitativas (ej. 'sedentario activo') e identificar perfiles de riesgo. | CU-10 |
| **RF19** | Media | Combinación con datos de clima | Integrar datos del clima y calidad del aire para ajustar alertas de riesgo en crónicos. | CU-09 |
| **RF20** | Alta | Predicción de saturación de urgencias | Predecir saturación mediante redes neuronales con $\ge 4$ horas de anticipación, nivel de confianza y variables explicativas. | CU-12 |
| **RF21** | Media | Alertas escalonadas | Emitir alertas de ocupación y riesgo en pacientes, con escalonamiento por canal (panel, jefe, dirección). | CU-07, CU-11 |
| **RF22** | Media | Simulador de eventos masivos | Simular eventos masivos con datos sintetizados para estimar recursos y apoyar planes de contingencia. | CU-13 |
| **RF23** | Media | Modo contingencia offline (Edge) | Nodos de borde deben almacenar eventos IoT localmente ante caídas de red y sincronizar al restaurar conexión. | CU-28 |
| **RF24** | Media | Verificación de integridad documental | Permitir a usuarios verificar que un documento no fue alterado desde su firma (apoyado en blockchain). | CU-22 |
| **RF25** | Media | Reportes gerenciales | Generar reportes periódicos de historias, solicitudes, tiempos, resúmenes y trazabilidad. | CU-26 |
| **RF26** | Media | Portal y aplicación del paciente | Ofrecer portal/app al paciente para consultar diagnósticos, tratamientos y resúmenes previa verificación. | CU-25 |
| **RF27** | Media | Configuración de umbrales | Permitir a usuarios autorizados configurar umbrales de alerta y parámetros sin soporte de desarrollo. | CU-06 |
| **RF28** | Media | Gestión de usuarios y clínica | Administrador puede gestionar usuarios y la base de conocimiento clínico con importación/validación. | CU-02, CU-30 |

---

## 2. Requerimientos No Funcionales (RNF)

| ID | Atributo | Descripción | Métrica / Objetivo |
| :--- | :--- | :--- | :--- |
| **RNF01** | Rendimiento (IoT) | Ingesta de datos IoT con baja latencia. | $< 2$ s por evento |
| **RNF02** | Rendimiento (Voz a Texto) | Conversión de voz a texto debe responder rápidamente. | $< 3$ s / comando |
| **RNF03** | Rendimiento (Predicción IA) | Predicción calculada anticipadamente y con alta exactitud. | $\ge 4$ h anticipación, exactitud $\ge 85\%$ |
| **RNF04** | Rendimiento (Búsqueda) | Búsqueda de historias clínicas y resúmenes. | $< 3$ s / consulta |
| **RNF05** | Disponibilidad | Sistema estable en crisis; sin pérdida de datos en modo offline. | Uptime $\ge 99.9\%$, 0 pérdida datos offline |
| **RNF06** | Capacidad ingesta | Soportar picos de eventos IoT en emergencias sin degradarse. | $\ge 100$ eventos/s en pico |
| **RNF07** | Escalabilidad | Escalar horizontalmente para soportar crecimiento (hospitales/sensores). | Escalado horizontal probado |
| **RNF08** | Seguridad (Datos) | Comunicación cifrada y datos en reposo cifrados. | TLS + AES-256 en reposo |
| **RNF09** | Seguridad (Acceso) | Autenticación, autorización por roles (RBAC) y auditoría. | JWT/OAuth + RBAC + auditoría |
| **RNF10** | Privacidad | Tratamiento de datos de salud bajo normativas legales. | Cumplimiento normativo verificado |
| **RNF11** | Interoperabilidad | Historias clínicas bajo estándar HL7/FHIR para integración. | $0$ fallos de formato FHIR |
| **RNF12** | Exactitud Reconocimiento | Alta precisión en voz a texto con vocabulario médico. | WER $< 5\%$ |
| **RNF13** | Integridad | Transacciones inmutables y verificables (Blockchain). | Registro inmutable + verificación |
| **RNF14** | Respaldo/Recuperación | Respaldo continuo ante desastres. | $RPO \le 15$ min, $RTO \le 2$ h |
| **RNF15** | Usabilidad | Interfaces intuitivas de mínimos clics. | $\le 3$ clics / tarea principal |
| **RNF16** | Mantenibilidad | Código modular, APIs documentadas y pruebas. | Cobertura pruebas + despliegue continuo|
| **RNF17** | Portabilidad | Compatibilidad con navegadores y dispositivos móviles (Cloud). | Compatibilidad multiplataforma |
| **RNF18** | Fiabilidad Integraciones | Reintentos y degradación controlada en API externas. | Reintentos + degradación controlada |

---

## 3. HISTORIAS DE USUARIO - PROYECTO MIMETIC

## HU-MIMETIC-001
* **Rol**: Como Médica Internista[cite: 34]
* **Característica / Funcionalidad**: Necesito un asistente conversacional que interprete síntomas en lenguaje natural, sugiera diagnósticos diferenciales con dosis ajustadas y genere reportes en PDF.[cite: 34]
* **Razón / Resultado**: Con la finalidad de optimizar la toma de decisiones clínicas, disminuir olvidos diagnósticos y emitir historias clínicas exportables.[cite: 34]
* **Criterios de Aceptación**:
  1. **Sugerencia de diagnósticos diferenciales**: En caso que la médica ingrese o dicte los síntomas del paciente[cite: 34], cuando consulte al asistente clínico[cite: 34], el sistema retornará diagnósticos diferenciales con nivel de confianza y preguntas discriminatorias.[cite: 34]
  2. **Ajuste posológico por perfil**: En caso que se formule un tratamiento médico[cite: 34], cuando el sistema valide el perfil del paciente[cite: 34], el sistema sugerirá la dosis ajustada según peso, alergias, embarazo y comorbilidades.[cite: 34]
  3. **Exportación de Historia Clínica a PDF**: En caso que se requiera el documento descargable o impreso de la consulta[cite: 34], cuando la médica seleccione 'Generar PDF'[cite: 34], el sistema compilará la atención en un PDF estandarizado listo para imprimir o enviar.[cite: 34]

## HU-MIMETIC-002
* **Rol**: Como Médica Internista[cite: 34]
* **Característica / Funcionalidad**: Necesito dictar notas de evolución, órdenes clínicas y fórmulas médicas mediante comandos de voz para su transcripción y estructuración automática.[cite: 34]
* **Razón / Resultado**: Con la finalidad de reducir el 40% del tiempo dedicado a labores administrativas frente al computador y centrarme en la atención clínica directa.[cite: 34]
* **Criterios de Aceptación**:
  1. **Transcripción veloz de voz a texto**: En caso que la médica active el dictado por voz durante la consulta[cite: 34], cuando pronuncie un comando u observación clínica[cite: 34], el sistema compilará la información en un borrador estructurado en menos de 3 segundos con un error de palabras (WER) < 5%.[cite: 34]
  2. **Validación clínica y dosis inusuales**: En caso que el sistema detecte un término ambiguo o una dosis que exceda el rango seguro[cite: 34], cuando la médica intente guardar la nota[cite: 34], el sistema solicitará confirmación explícita mediante una alerta contextual antes de confirmar el guardado.[cite: 34]
  3. **Almacenamiento bajo HL7/FHIR**: En caso que la nota clínica sea confirmada por la médica[cite: 34], cuando se guarde en la base de datos PostgreSQL[cite: 34], el sistema estructurará y almacenará la historia clínica bajo el estándar HL7/FHIR con 0 errores de formato.[cite: 34]

## HU-MIMETIC-003
* **Rol**: Como Médico de Triaje / Encargado de Admisiones[cite: 34]
* **Característica / Funcionalidad**: Necesito solicitar camillas, quirófanos y traslados mediante un formulario digital directo desde el módulo de triaje.[cite: 34]
* **Razón / Resultado**: Con la finalidad de eliminar el trámite físico en papel que toma hasta 45 minutos por paciente y agilizar la asignación de recursos.[cite: 34]
* **Criterios de Aceptación**:
  1. **Solicitud digital sin papel**: En caso que el médico requiera asignar una camilla o quirófano desde triaje[cite: 34], cuando presione el botón "Solicitar Recurso"[cite: 34], la orden se transmitirá al instante al panel de Admisiones/Archivo sin impresiones físicas.[cite: 34]
  2. **Vinculación a Historia Clínica**: En caso que se genere una solicitud digital de traslado o recurso[cite: 34], cuando la solicitud sea creada[cite: 34], el sistema vinculará automáticamente el registro a la historia clínica del paciente en menos de 2 segundos.[cite: 34]
  3. **Visibilidad del estado del trámite**: En caso que el personal de admisión o enfermería consulte la solicitud[cite: 34], cuando se actualice el flujo de atención[cite: 34], el sistema mostrará el estado actualizado del trámite en tiempo real para todos los involucrados.[cite: 34]

## HU-MIMETIC-004
* **Rol**: Como Director de Urgencias[cite: 34]
* **Característica / Funcionalidad**: Necesito recibir predicciones de saturación de urgencias con 4 horas de anticipación y notificaciones escalonadas configurables.[cite: 34]
* **Razón / Resultado**: Con la finalidad de habilitar camas de transición, acelerar altas y reorganizar el personal antes del colapso, evitando la fatiga por alertas.[cite: 34]
* **Criterios de Aceptación**:
  1. **Predicción anticipada de saturación**: En caso que las tendencias de ingreso y ocupación sugieran saturación[cite: 34], cuando ejecute el algoritmo predictivo de redes neuronales[cite: 34], el sistema notificará la saturación con al menos 4 horas de anticipación y exactitud mayor o igual a 85%.[cite: 34]
  2. **Explicabilidad del modelo predictivo**: En caso que se genere una alerta de saturación[cite: 34], cuando el director consulte el detalle predictivo[cite: 34], el sistema mostrará el nivel de confianza y las variables causales determinantes que la dispararon.[cite: 34]
  3. **Escalonamiento de alertas**: En caso que se superen los umbrales de ocupación configurados (ej. > 90%)[cite: 34], cuando la condición crítica persista[cite: 34], el sistema notificará primero al panel, luego al jefe de turno y finalmente a la dirección.[cite: 34]

## HU-MIMETIC-005
* **Rol**: Como Paciente de la clínica[cite: 34]
* **Característica / Funcionalidad**: Necesito acceder a un portal web o aplicación móvil tras verificar mi identidad para consultar la vista de mis diagnósticos, fórmulas médicas, tratamientos prescritos, resúmenes de atención y notificaciones.[cite: 34]
* **Razón / Resultado**: Con la finalidad de tener visibilidad clara de mi historial de salud, comprender mis recomendaciones y cumplir con el tratamiento y medicación indicada sin requerir desplazamientos al archivo.[cite: 34]
* **Criterios de Aceptación**:
  1. **Autenticación y acceso al portal**: En caso que el paciente ingrese al portal o app[cite: 34], cuando verifique su identidad de forma segura[cite: 34], el sistema le dará acceso a su perfil clínico personalizado.[cite: 34]
  2. **Consulta de diagnósticos y tratamientos**: En caso que el paciente consulte el módulo de atenciones[cite: 34], cuando seleccione una consulta o alta médica[cite: 34], el sistema desplegará en lenguaje sencillo sus diagnósticos confirmados, indicaciones y plan de manejo.[cite: 34]
  3. **Vista de fórmulas clínicas y medicinas**: En caso que el paciente revise sus medicamentos prescritos[cite: 34], cuando ingrese a la sección de fórmulas[cite: 34], el sistema mostrará las medicinas formuladas, dosis ajustadas, frecuencia de toma y recomendaciones de alarma.[cite: 34]

## HU-MIMETIC-006
* **Rol**: Como Médica Internista[cite: 34]
* **Característica / Funcionalidad**: Necesito monitorear biométricos de pacientes post-alta mediante wearables, clasificar sus hábitos cualitativamente e integrar variables climáticas.[cite: 34]
* **Razón / Resultado**: Con la finalidad de anticipar descompensaciones en pacientes crónicos (hipertensión, EPOC) e intervenir antes de un reingreso de emergencia.[cite: 34]
* **Criterios de Aceptación**:
  1. **Captura de biométricos desde wearables**: En caso que el paciente post-alta utilice una pulsera inteligente registrada[cite: 34], cuando el dispositivo transmita pulso y acelerometría[cite: 34], el sistema almacenará y analizará las métricas de frecuencia cardíaca, variabilidad y reposo.[cite: 34]
  2. **Clasificación cualitativa de hábitos**: En caso que el sistema detecte caminata alta con prolongada inactividad sentada[cite: 34], cuando procese el acumulado diario[cite: 34], el sistema asignará la etiqueta "sedentario activo" y alertará sobre el factor de riesgo oculto.[cite: 34]
  3. **Integración con API de Clima**: En caso de olas de calor, cambios bruscos de temperatura o mala calidad del aire[cite: 34], cuando el sistema consulte OpenWeatherMap API[cite: 34], el sistema cruzará la condición ambiental con la patología del paciente y ajustará las alertas de riesgo.[cite: 34]

## HU-MIMETIC-007
* **Rol**: Como Encargado de Archivo y Auditor Clínico[cite: 34]
* **Característica / Funcionalidad**: Necesito aplicar firma electrónica y registrar de forma inmutable las transacciones y cambios documentales en Blockchain.[cite: 34]
* **Razón / Resultado**: Con la finalidad de otorgar validez jurídica, evitar la alteración silenciosa de expedientes y certificar la integridad documental ante auditorías.[cite: 34]
* **Criterios de Aceptación**:
  1. **Estampado de firma electrónica**: En caso que se autorice una orden, consentimiento o resumen de alta[cite: 34], cuando el usuario aplique su firma[cite: 34], el sistema vinculará la identidad digital, marca de tiempo y hash del documento garantizando validez legal.[cite: 34]
  2. **Registro inmutable en Blockchain**: En caso que se genere o modifique un registro clínico[cite: 34], cuando se guarde la transacción[cite: 34], el sistema inscribirá la transacción de forma inmutable en la red Blockchain para auditoría posterior.[cite: 34]
  3. **Verificación de integridad documental**: En caso de requerirse validar que un documento no ha sido alterado[cite: 34], cuando se ejecute la verificación de integridad[cite: 34], el sistema cotejará el hash actual contra Blockchain y responderá en menos de 3 segundos confirmando su autenticidad.[cite: 34]
  4. **Trazabilidad completa de auditoría**: En caso de auditar las modificaciones de una historia clínica[cite: 34], cuando se consulte el historial de cambios[cite: 34], el sistema mostrará la secuencia de quién modificó, qué campos, la fecha y el rol del usuario sin permitir borrados.[cite: 34]

## HU-MIMETIC-008
* **Rol**: Como Encargado de Archivo / Paciente[cite: 34]
* **Característica / Funcionalidad**: Necesito realizar búsquedas inmediatas de historias clínicas y disponer de un resumen de alta accesible en lenguaje sencillo vía correo o app.[cite: 34]
* **Razón / Resultado**: Con la finalidad de garantizar la rápida localización de expedientes y asegurar que el paciente comprenda su tratamiento y señales de alarma.[cite: 34]
* **Criterios de Aceptación**:
  1. **Búsqueda ágil de expedientes**: En caso que el usuario de archivo o médico busque una historia clínica[cite: 34], cuando ingrese el documento, nombre, servicio o rango de fechas[cite: 34], el sistema devolverá los expedientes coincidentes en un tiempo menor a 3 segundos.[cite: 34]
  2. **Generación y envío del resumen de alta**: En caso que el médico otorgue el alta al paciente[cite: 34], cuando se confirme el cierre de atención[cite: 34], el sistema enviará automáticamente un resumen en lenguaje claro al correo/app del paciente registrando la entrega.[cite: 34]

## HU-MIMETIC-009
* **Rol**: Como Director de Urgencias[cite: 34]
* **Característica / Funcionalidad**: Necesito simular eventos masivos con datos sintetizados para estimar la demanda de recursos hospitalarios y preparar planes de contingencia.[cite: 34]
* **Razón / Resultado**: Con la finalidad de entrenar al personal, anticipar cuellos de botella ante emergencias reales y sustentar solicitudes de equipamiento.[cite: 34]
* **Criterios de Aceptación**:
  1. **Ejecución de simulación de desastres**: En caso que se programe un simulacro de emergencia[cite: 34], cuando se configure y ejecute el simulador[cite: 34], el sistema modelará la llegada progresiva, velocidad de llenado de camas y consumo de insumos.[cite: 34]
  2. **Reporte de cuellos de botella**: En caso que la simulación finalice[cite: 34], cuando el sistema procese el modelo[cite: 34], el sistema generará un informe visual destacando los puntos de colapso y necesidades proyectadas.[cite: 34]

## HU-MIMETIC-010
* **Rol**: Como Administrador del Sistema[cite: 34]
* **Característica / Funcionalidad**: Necesito administrar usuarios, roles y permisos (RBAC) mediante JWT/OAuth y gestionar la base de conocimiento clínico.[cite: 34]
* **Razón / Resultado**: Con la finalidad de restringir el acceso a datos de salud según el perfil y mantener actualizada la base de patologías y tratamientos.[cite: 34]
* **Criterios de Aceptación**:
  1. **Autenticación segura y RBAC**: En caso que un usuario intente acceder al sistema[cite: 34], cuando se autentique mediante JWT/OAuth[cite: 34], el sistema validará el perfil y habilitará únicamente sus funciones autorizadas.[cite: 34]
  2. **Gestión de conocimiento clínico**: En caso que el administrador requiera actualizar información médica[cite: 34], cuando cargue o edite datos sintomáticos o farmacéuticos[cite: 34], el sistema validará e importará el conocimiento estructurado para uso de los módulos de IA.[cite: 34]

## HU-MIMETIC-011
* **Rol**: Como Director de Urgencias / Auditor[cite: 34]
* **Característica / Funcionalidad**: Necesito configurar dinámicamente umbrales de alerta e indicadores, y generar reportes gerenciales con estadísticas de atención.[cite: 34]
* **Razón / Resultado**: Con la finalidad de adaptar el comportamiento del gemelo digital a necesidades cambiantes y presentar datos auditables a la gerencia.[cite: 34]
* **Criterios de Aceptación**:
  1. **Configuración de umbrales**: En caso que la dirección requiera modificar límites de tiempo o saturación[cite: 34], cuando actualice los valores en la interfaz administrativa[cite: 34], el sistema ajustará las reglas de disparo de alertas de inmediato sin reescribir código.[cite: 34]
  2. **Generación de reportes gerenciales**: En caso que se requiera el balance de gestión mensual para gerencia o auditoría[cite: 34], cuando el usuario solicite el reporte estadístico[cite: 34], el sistema exportará métricas de historias creadas, trámites, resúmenes entregados y tiempos de espera.[cite: 34]

## HU-MIMETIC-012
* **Rol**: Como Director de Urgencias[cite: 34]
* **Característica / Funcionalidad**: Necesito visualizar en tiempo real la ubicación y estado (libre, ocupado, en limpieza, mantenimiento) de camas, camillas y quirófanos mediante sensores IoT.[cite: 34]
* **Razón / Resultado**: Con la finalidad de eliminar la búsqueda manual de recursos, optimizar el flujo hospitalario y reducir la cancelación de cirugías por falta de espacio.[cite: 34]
* **Criterios de Aceptación**:
  1. **Actualización en tiempo real**: En caso que un sensor IoT detecte un cambio de estado en una camilla o cama[cite: 34], cuando el sensor emita la señal al sistema[cite: 34], el sistema reflejará el cambio en el panel en menos de 2 segundos y registrará el log en MongoDB.[cite: 34]
  2. **Refresco automático del Dashboard**: En caso que el usuario consulte el panel de control durante la operación normal[cite: 34], cuando transcurran entre 5 y 10 segundos[cite: 34], el sistema actualizará automáticamente los indicadores de ocupación, tiempos de espera y cancelaciones.[cite: 34]
  3. **Ingesta masiva en emergencias**: En caso de presentarse un evento masivo con picos de ingesta de hasta 100 eventos por segundo[cite: 34], cuando los sensores envíen transmisiones concurrentes[cite: 34], el sistema almacenará el 100% de los logs con marca de tiempo sin caídas ni degradación de interfaz.[cite: 34]
  4. **Monitoreo de salud del hardware**: En caso que un sensor IoT presente batería baja o pérdida de señal[cite: 34], cuando el dispositivo reporte el fallo[cite: 34], el sistema emitirá una alerta de mantenimiento y degradará el estado de forma controlada sin inventar datos.[cite: 34]

## HU-MIMETIC-013
* **Rol**: Como Administrador / Ingeniero de Soporte[cite: 34]
* **Característica / Funcionalidad**: Necesito que los nodos de borde (Edge Computing) almacenen localmente los eventos IoT ante fallas de conectividad y los sincronicen al restaurar la red.[cite: 34]
* **Razón / Resultado**: Con la finalidad de garantizar cero pérdida de información crítica del hospital durante contingencias o caídas del servicio de internet.[cite: 34]
* **Criterios de Aceptación**:
  1. **Conmutación a modo offline**: En caso de detectarse una pérdida de red o congestión en el hospital[cite: 34], cuando falle la comunicación central[cite: 34], los nodos Edge filtrarán y almacenarán localmente todos los registros IoT sin pérdida de datos.[cite: 34]
  2. **Sincronización automática de datos**: En caso que la conectividad a la red principal sea reestablecida[cite: 34], cuando se detecte la reconexión[cite: 34], el sistema transferirá automáticamente los logs acumulados a MongoDB resolviendo duplicidades.[cite: 34]