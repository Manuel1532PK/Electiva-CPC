import type { FieldConfig, Message } from './types'

export const IDENTIFICATION_FIELDS: FieldConfig[] = [
  { key: 'first_name', label: 'Nombres', placeholder: 'Ej: Juan Andrés' },
  { key: 'last_name', label: 'Apellidos', placeholder: 'Ej: Pérez García' },
  { key: 'document_type', label: 'Tipo de documento', type: 'select', options: [
    { value: 'CC', label: 'Cédula de Ciudadanía (CC)' },
    { value: 'TI', label: 'Tarjeta de Identidad (TI)' },
    { value: 'CE', label: 'Cédula de Extranjería (CE)' },
    { value: 'RC', label: 'Registro Civil (RC)' },
    { value: 'Pasaporte', label: 'Pasaporte' },
  ]},
  { key: 'id_document', label: 'Número de documento', placeholder: 'Ej: 123456789' },
  { key: 'birth_date', label: 'Fecha de nacimiento', placeholder: 'DD/MM/AAAA' },
  { key: 'age', label: 'Edad', placeholder: 'Ej: 45', suffix: 'años' },
  { key: 'gender', label: 'Género', type: 'select', options: [
    { value: 'M', label: 'Masculino' },
    { value: 'F', label: 'Femenino' },
    { value: 'Otro', label: 'Otro' },
  ]},
  { key: 'occupation', label: 'Ocupación', placeholder: 'Ej: Ingeniero' },
  { key: 'phone', label: 'Teléfono', placeholder: 'Ej: 3001234567' },
  { key: 'country', label: 'País', placeholder: 'Ej: Colombia' },
  { key: 'department', label: 'Departamento', placeholder: 'Ej: Cundinamarca' },
  { key: 'city', label: 'Ciudad de residencia', placeholder: 'Ej: Bogotá' },
]

export const ANAMNESIS_FIELDS: FieldConfig[] = [
  { key: 'consultation_reason', label: 'Motivo de consulta', placeholder: 'Describe brevemente el motivo' },
  { key: 'symptom_evolution', label: 'Tiempo de evolución', placeholder: 'Ej: 3 días', suffix: 'días/semanas' },
]

export const ANTECEDENTES_FIELDS: FieldConfig[] = [
  { key: 'tobacco', label: 'Consumo de tabaco', type: 'select', options: [
    { value: '', label: '-- Seleccionar --' },
    { value: 'No', label: 'No fuma' },
    { value: 'Ocasionalmente', label: 'Ocasionalmente' },
    { value: 'A diario', label: 'Fuma a diario' },
    { value: 'Exfumador', label: 'Exfumador' },
  ]},
  { key: 'alcohol', label: 'Consumo de alcohol', type: 'select', options: [
    { value: '', label: '-- Seleccionar --' },
    { value: 'No', label: 'No consume' },
    { value: '1-2 veces/semana', label: '1-2 veces por semana' },
    { value: '3-5 veces/semana', label: '3-5 veces por semana' },
    { value: 'A diario', label: 'A diario' },
  ]},
  { key: 'substances', label: 'Uso de sustancias', type: 'select', options: [
    { value: '', label: '-- Seleccionar --' },
    { value: 'No', label: 'Ninguna' },
    { value: 'Cannabis', label: 'Cannabis' },
    { value: 'Cocaína', label: 'Cocaína' },
    { value: 'Otras', label: 'Otras' },
  ]},
  { key: 'physical_activity', label: 'Actividad física en el último mes', type: 'select', options: [
    { value: 'Sedentario', label: 'Sedentario (poco o ningún ejercicio)' },
    { value: '1-2 veces/semana', label: '1-2 veces por semana' },
    { value: '3+ veces/semana', label: '3 o más veces por semana' },
    { value: 'Diario', label: 'Ejercicio diario' },
  ]},
  { key: 'pregnancy', label: '¿Está embarazada?', type: 'select', condition: (info) => info.gender === 'F', options: [
    { value: '', label: '-- Seleccionar --' },
    { value: 'true', label: 'Sí' },
    { value: 'false', label: 'No' },
  ]},
  { key: 'medical_history', label: 'Antecedentes médicos', placeholder: 'Diabetes, HTA, etc.' },
  { key: 'surgical_history', label: 'Antecedentes quirúrgicos', placeholder: 'Cirugías previas' },
  { key: 'pharmacological_history', label: 'Antecedentes farmacológicos', placeholder: 'Medicamentos actuales' },
  { key: 'allergies', label: 'Alergias conocidas', placeholder: 'Medicamentos, alimentos, etc.' },
]

export const SIGNOS_FIELDS: FieldConfig[] = [
  { key: 'blood_pressure', label: 'Presión arterial (PA)', placeholder: 'Ej: 120/80', suffix: 'mmHg' },
  { key: 'heart_rate', label: 'Frecuencia cardíaca (FC)', placeholder: 'Ej: 72', suffix: 'lpm' },
  { key: 'respiratory_rate', label: 'Frecuencia respiratoria (FR)', placeholder: 'Ej: 16', suffix: 'rpm' },
  { key: 'temperature', label: 'Temperatura', placeholder: 'Ej: 36.5', suffix: '°C' },
  { key: 'oxygen_saturation', label: 'Saturación de oxígeno (SpO2)', placeholder: 'Ej: 97', suffix: '%' },
  { key: 'weight', label: 'Peso', placeholder: 'Ej: 70', suffix: 'kg' },
  { key: 'height', label: 'Estatura', placeholder: 'Ej: 170', suffix: 'cm' },
]

export const TRIAJE_FIELDS: FieldConfig[] = [
  { key: 'triage_level', label: 'Nivel de triaje', type: 'select', options: [
    { value: '1', label: 'Nivel 1 — Rojo (Atención inmediata)' },
    { value: '2', label: 'Nivel 2 — Naranja (Emergencia)' },
    { value: '3', label: 'Nivel 3 — Amarillo (Urgente)' },
    { value: '4', label: 'Nivel 4 — Verde (Estándar)' },
    { value: '5', label: 'Nivel 5 — Azul (No urgente)' },
  ]},
  { key: 'triage_system', label: 'Sistema de triaje', type: 'select', options: [
    { value: 'Manchester', label: 'Manchester (MTS)' },
    { value: 'ESI', label: 'Emergency Severity Index (ESI)' },
  ]},
  { key: 'triage_score', label: 'Puntuación de gravedad', placeholder: 'Ej: NEWS2 = 6 · CURB-65 = 2' },
  { key: 'triage_discriminators', label: 'Discriminadores de triaje', placeholder: 'Disnea en reposo, taquipnea, SpO2 93%...' },
]

export const LAB_FIELDS: FieldConfig[] = [
  { key: 'lab_pao2', label: 'pO₂ arterial', placeholder: 'Ej: 68', suffix: 'mmHg' },
  { key: 'lab_lactate', label: 'Lactato', placeholder: 'Ej: 2.1', suffix: 'mmol/L' },
  { key: 'lab_leukocytes', label: 'Leucocitos', placeholder: 'Ej: 14.2', suffix: '10³/µL' },
  { key: 'lab_creatinine', label: 'Creatinina', placeholder: 'Ej: 1.0', suffix: 'mg/dL' },
  { key: 'lab_crp', label: 'Proteína C reactiva', placeholder: 'Ej: 82', suffix: 'mg/L' },
]

export const FULL_GROUPS = [
  { title: 'Identificación del Paciente', fields: IDENTIFICATION_FIELDS },
  { title: 'Anamnesis', fields: ANAMNESIS_FIELDS },
  { title: 'Antecedentes Personales', fields: ANTECEDENTES_FIELDS },
  { title: 'Signos Vitales', fields: SIGNOS_FIELDS },
  { title: 'Triaje Manchester / ESI', fields: TRIAJE_FIELDS },
  { title: 'Laboratorio Urgente', fields: LAB_FIELDS },
]

export const SESSION_GROUPS = [
  { title: 'Anamnesis', fields: ANAMNESIS_FIELDS },
  { title: 'Antecedentes Personales', fields: ANTECEDENTES_FIELDS },
  { title: 'Signos Vitales', fields: SIGNOS_FIELDS },
  { title: 'Triaje Manchester / ESI', fields: TRIAJE_FIELDS },
  { title: 'Laboratorio Urgente', fields: LAB_FIELDS },
]

export const SECTION_ICONS = ['📋', '💬', '📄', '🩺', '🚦', '🧪']

export const INITIAL_MESSAGES: Message[] = [
  { id: '0', role: 'assistant', text: 'Hola, soy Mimetic AI. Antes de comenzar, necesito los datos del paciente.' },
]