import { apiFetch, errorMessage } from './client'

export interface ClinicalHistory {
  id: string
  document_number: string
  document_type: string
  first_name: string
  last_name: string
  birth_date: string
  age: string
  gender: string
  occupation: string
  phone: string
  country: string
  department: string
  city: string
  created_at: string
  updated_at: string
}

export interface PatientSession {
  id: string
  document_number: string
  doctor_id: string
  doctor_name: string
  hospital_id: string
  hospital_name: string
  date: string
  consultation_reason: string
  symptom_evolution: string
  tobacco: string
  alcohol: string
  substances: string
  physical_activity: string
  pregnancy: string
  medical_history: string
  surgical_history: string
  pharmacological_history: string
  allergies: string
  blood_pressure: string
  heart_rate: string
  respiratory_rate: string
  temperature: string
  weight: string
  height: string
  symptoms: string[]
  diagnoses: { disease_name: string; description?: string; severity?: string; confidence?: number }[]
  treatment: {
    disease_name: string
    available?: { name: string; dosage?: string; frequency?: string; duration?: string; route?: string; patient_summary?: string }[]
    medicines?: { name: string; dosage?: string; frequency?: string; duration?: string; route?: string; patient_summary?: string }[]
    general_recommendations?: string
    non_pharmacological?: string[]
    non_pharmacological_treatments?: string[]
  } | null
  report_html: string
  doctor_review?: Record<string, unknown>
}

export interface PatientSessionSummary {
  id: string
  date: string
  hospital_name: string
  doctor_name: string
  consultation_reason: string
  diagnoses: { disease_name: string; description?: string; severity?: string }[]
  has_treatment: boolean
  symptoms: string[]
}

export interface PatientTreatment {
  disease_name: string
  medicines: { name: string; dosage?: string; frequency?: string; duration?: string; route?: string; patient_summary?: string }[]
  general_recommendations: string
  session_date: string
  hospital_name: string
}

export interface PatientSummary {
  total_sessions: number
  total_diagnoses: number
  hospitals_visited: string[]
  last_session_date: string | null
  last_diagnosis: string | null
  recent_sessions: PatientSessionSummary[]
}

export async function getMyClinicalHistory(): Promise<ClinicalHistory | null> {
  const res = await apiFetch('/api/patient/clinical-history')
  if (res.status === 404) return null
  if (!res.ok) throw new Error(await errorMessage(res, 'Error al cargar historia clínica'))
  return res.json()
}

export async function getMySessions(): Promise<PatientSession[]> {
  const res = await apiFetch('/api/patient/sessions')
  if (!res.ok) throw new Error(await errorMessage(res, 'Error al cargar sesiones'))
  return res.json()
}

export async function getMySessionDetail(sessionId: string): Promise<PatientSession> {
  const res = await apiFetch(`/api/patient/sessions/${sessionId}`)
  if (!res.ok) throw new Error(await errorMessage(res, 'Error al cargar la sesión'))
  return res.json()
}

export async function getMyTreatments(): Promise<PatientTreatment[]> {
  const res = await apiFetch('/api/patient/treatments')
  if (!res.ok) throw new Error(await errorMessage(res, 'Error al cargar tratamientos'))
  return res.json()
}

export async function getMySummary(): Promise<PatientSummary> {
  const res = await apiFetch('/api/patient/summary')
  if (!res.ok) throw new Error(await errorMessage(res, 'Error al cargar resumen'))
  return res.json()
}
