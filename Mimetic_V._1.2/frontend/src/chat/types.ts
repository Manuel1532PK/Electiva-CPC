export type Message = {
  id: string
  role: 'user' | 'assistant'
  text: string
  suggestions?: string[]
  diagnoses?: Diagnosis[]
  treatment?: Treatment
  excluded_symptoms?: string[]
}

export type Diagnosis = {
  disease_name: string
  description: string
  severity: string
  confidence: number
  matched_symptoms: number
  total_input_symptoms: number
  present_symptoms?: string[]
  missing_key_symptoms?: string[]
}

export type ManualDiagnosis = {
  id: string
  disease_name: string
  notes?: string
}

export type DoctorReview = {
  confirmedDiagnoses: string[]
  rejectedDiagnoses: string[]
  manualDiagnoses: ManualDiagnosis[]
  selectedMedicines: string[]
  modifiedDoses: Record<string, string>
  doctorNotes: string
}

export type MedicineDetail = {
  name: string
  dosage?: string
  dosage_mg_kg?: string | null
  max_daily_dose?: string
  frequency?: string
  duration?: string
  route?: string
  calculated_dosage?: string
  reasons?: string[]
  contraindications?: {
    conditions: string[]
    allergies: string[]
    comorbidities: string[]
  }
  adjustments?: {
    renal: string
    hepatic: string
    pediatric: string
    geriatric: string
    pregnancy: string
  }
  interactions_warning?: string
  monitoring?: string
  patient_summary?: string
}

export type Treatment = {
  disease_name: string
  medicines?: MedicineDetail[]
  general_recommendations: string
  available?: MedicineDetail[]
  not_recommended?: MedicineDetail[]
  alternatives?: MedicineDetail[]
  non_pharmacological?: string[]
}

export type PatientInfo = {
  first_name?: string
  last_name?: string
  name?: string
  document_type?: string
  id_document?: string
  birth_date?: string
  age?: string
  gender?: string
  occupation?: string
  phone?: string
  location?: string
  country?: string
  department?: string
  city?: string
  consultation_reason?: string
  symptom_evolution?: string
  tobacco?: string
  alcohol?: string
  substances?: string
  physical_activity?: string
  pregnancy?: string
  medical_history?: string
  surgical_history?: string
  pharmacological_history?: string
  allergies?: string
  blood_pressure?: string
  heart_rate?: string
  respiratory_rate?: string
  temperature?: string
  oxygen_saturation?: string
  weight?: string
  height?: string
  triage_level?: string
  triage_system?: string
  triage_discriminators?: string
  triage_score?: string
  lab_pao2?: string
  lab_lactate?: string
  lab_leukocytes?: string
  lab_creatinine?: string
  lab_crp?: string
}

export type FieldConfig = {
  key: string
  label: string
  placeholder?: string
  type?: 'text' | 'select'
  options?: { value: string; label: string }[]
  suffix?: string
  condition?: (info: PatientInfo) => boolean
}

export type SearchResult = {
  document_number: string
  first_name: string
  last_name: string
  document_type: string
  source: string
  has_clinical_history: boolean
  has_user_account: boolean
  base_data: Record<string, string>
}

export type Phase = 'search' | 'patient_info' | 'symptoms' | 'report' | 'history'
export type PatientInfoMode = 'full' | 'session_only'

/** Identidad persistida en clinical_histories. */
export type ClinicalHistory = {
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
  created_at?: string
  updated_at?: string
}

/** Fila del landing del historial: paciente + actividad reciente. */
export type RecentPatient = {
  document_number: string
  first_name: string
  last_name: string
  age?: string
  gender?: string
  session_count: number
  documents: number
  last_session_date?: string
  last_reason?: string
  last_doctor?: string
}

/** Última sesión registrada del paciente: contexto de referencia, no se reenvía como datos actuales. */
export type SessionSnapshot = {
  id?: string
  date?: string
  doctor_name?: string
  hospital_name?: string
  consultation_reason?: string
  symptom_evolution?: string
  allergies?: string
  medical_history?: string
  surgical_history?: string
  pharmacological_history?: string
  blood_pressure?: string
  heart_rate?: string
  respiratory_rate?: string
  temperature?: string
  oxygen_saturation?: string
  weight?: string
  height?: string
  triage_level?: number
  triage_system?: string
  triage_discriminators?: string
  triage_score?: string
  labs?: Record<string, string>
  symptoms?: string[]
  diagnoses?: Diagnosis[]
  treatment?: Treatment | null
  report_html?: string
  doctor_review?: DoctorReview | null
}

export const INITIAL_DOCTOR_REVIEW: DoctorReview = {
  confirmedDiagnoses: [],
  rejectedDiagnoses: [],
  manualDiagnoses: [],
  selectedMedicines: [],
  modifiedDoses: {},
  doctorNotes: '',
}