import { useState, useRef, useEffect, useCallback } from 'react'
import { useAuth } from '../context/AuthContext'
import { apiFetch } from '../api/client'
import { extractError } from '../api/errors'
import { FULL_GROUPS, SESSION_GROUPS, INITIAL_MESSAGES } from './constants'
import type { ClinicalHistory, DoctorReview, Message, PatientInfo, PatientInfoMode, Phase, SearchResult, SessionSnapshot } from './types'
import { INITIAL_DOCTOR_REVIEW } from './types'

export function useChatApp() {
  const { user, logout } = useAuth()

  const [phase, setPhase] = useState<Phase>('search')
  const [patientInfoMode, setPatientInfoMode] = useState<PatientInfoMode>('full')
  const [messages, setMessages] = useState<Message[]>(INITIAL_MESSAGES)
  const [input, setInput] = useState('')
  const [isSending, setIsSending] = useState(false)
  const [isGeneratingReport, setIsGeneratingReport] = useState(false)
  const [currentSymptoms, setCurrentSymptoms] = useState<string[]>([])
  const [excludedSymptoms, setExcludedSymptoms] = useState<string[]>([])
  const [patientInfo, setPatientInfo] = useState<PatientInfo>({})
  const [reportHtml, setReportHtml] = useState<string | null>(null)
  const [formStep, setFormStep] = useState(0)
  const [selectedDiagnosis, setSelectedDiagnosis] = useState<string | null>(null)
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [selectedDocument, setSelectedDocument] = useState<string>('')
  const [lastSession, setLastSession] = useState<SessionSnapshot | null>(null)
  const [doctorReview, setDoctorReview] = useState<DoctorReview>({ ...INITIAL_DOCTOR_REVIEW })

  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState<SearchResult[]>([])
  const [showSearchResults, setShowSearchResults] = useState(false)
  const [searching, setSearching] = useState(false)
  const searchTimer = useRef<ReturnType<typeof setTimeout> | null>(null)

  const endRef = useRef<HTMLDivElement>(null)
  const searchRef = useRef<HTMLInputElement>(null)
  const sectionRefs = useRef<(HTMLDivElement | null)[]>([])
  const abortRef = useRef<AbortController | null>(null)

  const allFieldKeys = FULL_GROUPS.flatMap(g => g.fields.map(f => f.key))
  const sessionFieldKeys = SESSION_GROUPS.flatMap(g => g.fields.map(f => f.key))
  const fieldGroups = patientInfoMode === 'full' ? FULL_GROUPS : SESSION_GROUPS

  useEffect(() => {
    const el = endRef.current?.parentElement
    if (!el) return
    const isNearBottom = el.scrollHeight - el.scrollTop - el.clientHeight < 120
    if (isNearBottom) {
      endRef.current?.scrollIntoView({ behavior: 'smooth' })
    }
  }, [messages])

  useEffect(() => {
    if (phase === 'patient_info') {
      const el = sectionRefs.current[formStep]
      if (el) {
        const first = el.querySelector('input, select') as HTMLElement
        if (first) setTimeout(() => first.focus(), 100)
      }
    }
  }, [formStep, phase])

  useEffect(() => {
    if (phase === 'search' && searchRef.current) {
      searchRef.current.focus()
    }
  }, [phase])

  useEffect(() => {
    return () => abortRef.current?.abort()
  }, [])

  const doSearch = useCallback(async (q: string) => {
    if (!q || q.length < 1) {
      setSearchResults([])
      setShowSearchResults(false)
      return
    }
    setSearching(true)
    try {
      const res = await apiFetch(`/api/clinical-history/search?q=${encodeURIComponent(q)}`)
      if (res.ok) {
        const data: SearchResult[] = await res.json()
        setSearchResults(data)
        setShowSearchResults(true)
      }
    } catch {
      setSearchResults([])
    }
    setSearching(false)
  }, [])

  const handleSearchChange = (value: string) => {
    const digits = value.replace(/\D/g, '')
    setSearchQuery(digits)
    setShowSearchResults(true)
    if (searchTimer.current) clearTimeout(searchTimer.current)
    searchTimer.current = setTimeout(() => doSearch(digits), 200)
  }

  const selectPatient = async (result: SearchResult) => {
    setShowSearchResults(false)
    setSelectedDocument(result.document_number)
    setSearchQuery(`${result.document_number} — ${result.first_name} ${result.last_name}`)
    setLastSession(null)

    if (result.has_clinical_history) {
      setPatientInfoMode('session_only')
      const base = result.base_data
      setPatientInfo({
        first_name: base.first_name || result.first_name,
        last_name: base.last_name || result.last_name,
        name: `${base.first_name || result.first_name} ${base.last_name || result.last_name}`.trim(),
        document_type: base.document_type || result.document_type,
        id_document: result.document_number,
        birth_date: base.birth_date || '',
        age: base.age || '',
        gender: base.gender || '',
        phone: base.phone || '',
        country: base.country || '',
        department: base.department || '',
        city: base.city || '',
        location: base.city || '',
      })
      setPhase('patient_info')
      setFormStep(0)
      try {
        const res = await apiFetch(`/api/clinical-history/${result.document_number}/sessions`)
        if (res.ok) {
          const sessions: SessionSnapshot[] = await res.json()
          setLastSession(sessions[0] ?? null)
        }
      } catch {
        setLastSession(null)
      }
    } else if (result.has_user_account) {
      setPatientInfoMode('full')
      const base = result.base_data
      setPatientInfo({
        first_name: base.first_name || result.first_name,
        last_name: base.last_name || result.last_name,
        name: `${base.first_name || result.first_name} ${base.last_name || result.last_name}`.trim(),
        document_type: base.document_type || result.document_type,
        id_document: result.document_number,
        birth_date: base.birth_date || '',
        age: '',
        gender: '',
        occupation: '',
        phone: base.phone || '',
        country: base.country || '',
        department: base.department || '',
        city: base.city || '',
        location: base.city || '',
      })
      setPhase('patient_info')
      setFormStep(0)
    }
  }

  const startNewPatient = () => {
    setPatientInfoMode('full')
    setSelectedDocument('')
    setPatientInfo({})
    setSearchQuery('')
    setShowSearchResults(false)
    setPhase('patient_info')
    setFormStep(0)
    setLastSession(null)
  }

  /* ── Historial clínico (módulo persistido) ─────────────────────── */

  const openHistory = () => {
    setShowSearchResults(false)
    setPhase('history')
  }

  const resumeConsultation = () => {
    if (sessionId) setPhase('symptoms')
    else if (patientInfo.id_document) setPhase('patient_info')
    else setPhase('search')
  }

  /** Abre una nueva atención para un paciente ya existente, precargando identidad y última sesión. */
  const startConsultationFromHistory = async (documentNumber: string) => {
    const [historyRes, sessionsRes] = await Promise.all([
      apiFetch(`/api/clinical-history/${documentNumber}`),
      apiFetch(`/api/clinical-history/${documentNumber}/sessions`),
    ])
    if (!historyRes.ok) {
      throw new Error(await extractError(historyRes, 'No se pudo cargar la historia clínica.'))
    }
    const history: ClinicalHistory = await historyRes.json()
    const sessions: SessionSnapshot[] = sessionsRes.ok ? await sessionsRes.json() : []

    setSelectedDocument(documentNumber)
    setPatientInfoMode('session_only')
    setPatientInfo({
      first_name: history.first_name,
      last_name: history.last_name,
      name: `${history.first_name} ${history.last_name}`.trim(),
      document_type: history.document_type,
      id_document: documentNumber,
      birth_date: history.birth_date,
      age: history.age,
      gender: history.gender,
      phone: history.phone,
      country: history.country,
      department: history.department,
      city: history.city,
      location: history.city,
    })
    setLastSession(sessions[0] ?? null)
    setSessionId(null)
    setMessages(INITIAL_MESSAGES)
    setDoctorReview({ ...INITIAL_DOCTOR_REVIEW })
    setCurrentSymptoms([])
    setExcludedSymptoms([])
    setSelectedDiagnosis(null)
    setReportHtml(null)
    setSearchQuery(`${documentNumber} — ${history.first_name} ${history.last_name}`)
    setShowSearchResults(false)
    setFormStep(0)
    setPhase('patient_info')
  }

  const calculateAgeFromBirthDate = (birthDate: string): string => {
    if (!birthDate) return ''
    let parts = birthDate.split('/')
    if (parts.length === 3) {
      const day = parseInt(parts[0]), month = parseInt(parts[1]) - 1, year = parseInt(parts[2])
      const birth = new Date(year, month, day)
      if (isNaN(birth.getTime())) return ''
      const today = new Date()
      let age = today.getFullYear() - birth.getFullYear()
      const m = today.getMonth() - birth.getMonth()
      if (m < 0 || (m === 0 && today.getDate() < birth.getDate())) age--
      return age.toString()
    }
    parts = birthDate.split('-')
    if (parts.length === 3) {
      const year = parseInt(parts[0]), month = parseInt(parts[1]) - 1, day = parseInt(parts[2])
      const birth = new Date(year, month, day)
      if (isNaN(birth.getTime())) return ''
      const today = new Date()
      let age = today.getFullYear() - birth.getFullYear()
      const m = today.getMonth() - birth.getMonth()
      if (m < 0 || (m === 0 && today.getDate() < birth.getDate())) age--
      return age.toString()
    }
    return ''
  }

  const handlePatientFieldChange = (key: string, value: string) => {
    setPatientInfo(prev => {
      const updated = { ...prev, [key]: value }
      if (key === 'first_name' || key === 'last_name') {
        updated.name = `${updated.first_name || ''} ${updated.last_name || ''}`.trim()
      }
      if (key === 'city') {
        updated.location = value
      }
      if (key === 'birth_date') {
        const calculated = calculateAgeFromBirthDate(value)
        if (calculated) {
          updated.age = calculated
        }
      }
      return updated
    })
  }

  const submitPatientForm = async () => {
    setIsSending(true)
    try {
      const docNum = patientInfo.id_document || selectedDocument
      if (!docNum) throw new Error('Número de documento requerido')

      let currentSessionId: string | null = null

      if (patientInfoMode === 'full') {
        const histBody = {
          document_number: docNum,
          document_type: patientInfo.document_type || 'CC',
          first_name: patientInfo.first_name || '',
          last_name: patientInfo.last_name || '',
          birth_date: patientInfo.birth_date || '',
          age: patientInfo.age || '',
          gender: patientInfo.gender || '',
          occupation: patientInfo.occupation || '',
          phone: patientInfo.phone || '',
          country: patientInfo.country || '',
          department: patientInfo.department || '',
          city: patientInfo.city || '',
        }
        const histRes = await apiFetch('/api/clinical-history', {
          method: 'POST',
          body: JSON.stringify(histBody),
        })
        if (!histRes.ok) {
          const err = await extractError(histRes, 'Error al crear la historia clínica')
          throw new Error(err)
        }
      }

      const labs: Record<string, string> = {}
      if (patientInfo.lab_pao2?.trim()) labs.pao2 = patientInfo.lab_pao2.trim()
      if (patientInfo.lab_lactate?.trim()) labs.lactate = patientInfo.lab_lactate.trim()
      if (patientInfo.lab_leukocytes?.trim()) labs.leukocytes = patientInfo.lab_leukocytes.trim()
      if (patientInfo.lab_creatinine?.trim()) labs.creatinine = patientInfo.lab_creatinine.trim()
      if (patientInfo.lab_crp?.trim()) labs.crp = patientInfo.lab_crp.trim()

      const sessBody: Record<string, unknown> = {
        consultation_reason: patientInfo.consultation_reason || '',
        symptom_evolution: patientInfo.symptom_evolution || '',
        tobacco: patientInfo.tobacco || '',
        alcohol: patientInfo.alcohol || '',
        substances: patientInfo.substances || '',
        physical_activity: patientInfo.physical_activity || '',
        pregnancy: patientInfo.pregnancy || '',
        medical_history: patientInfo.medical_history || '',
        surgical_history: patientInfo.surgical_history || '',
        pharmacological_history: patientInfo.pharmacological_history || '',
        allergies: patientInfo.allergies || '',
        blood_pressure: patientInfo.blood_pressure || '',
        heart_rate: patientInfo.heart_rate || '',
        respiratory_rate: patientInfo.respiratory_rate || '',
        temperature: patientInfo.temperature || '',
        oxygen_saturation: patientInfo.oxygen_saturation || '',
        weight: patientInfo.weight || '',
        height: patientInfo.height || '',
        triage_level: patientInfo.triage_level ? parseInt(patientInfo.triage_level, 10) || 0 : 0,
        triage_system: patientInfo.triage_system || '',
        triage_discriminators: patientInfo.triage_discriminators || '',
        triage_score: patientInfo.triage_score || '',
        labs,
      }

      const sessRes = await apiFetch(`/api/clinical-history/${docNum}/sessions`, {
        method: 'POST',
        body: JSON.stringify(sessBody),
      })
      if (!sessRes.ok) {
        const err = await extractError(sessRes, 'Error al crear la sesión')
        throw new Error(err)
      }

      const sessData = await sessRes.json()
      currentSessionId = sessData.id
      setSessionId(currentSessionId)

      setMessages(m => [...m, {
        id: crypto.randomUUID(),
        role: 'assistant',
        text: 'Paciente registrado correctamente. Ahora describe los síntomas que presenta.',
      }])

      setPhase('symptoms')
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err)
      setMessages(m => [...m, { id: crypto.randomUUID(), role: 'assistant', text: msg }])
    }
    setIsSending(false)
  }

  const handleSend = async (textOverride?: string) => {
    const text = (textOverride || input).trim()
    if (!text || isSending) return
    if (!textOverride) setInput('')

    const userMsg: Message = { id: crypto.randomUUID(), role: 'user', text }
    setMessages(m => [...m, userMsg])

    if (abortRef.current) abortRef.current.abort()
    const controller = new AbortController()
    abortRef.current = controller

    setIsSending(true)
    try {
      const res = await apiFetch('/api/converse', {
        method: 'POST',
        signal: controller.signal,
        body: JSON.stringify({
          message: text,
          current_symptoms: currentSymptoms,
          excluded_symptoms: excludedSymptoms,
          patient_info: patientInfo,
        }),
      })
      if (!res.ok) {
        throw new Error(await extractError(res, 'No se pudo procesar tu mensaje.'))
      }
      const data = await res.json()

      if (data.normalized_symptoms && data.normalized_symptoms.length > 0) {
        setCurrentSymptoms(data.normalized_symptoms)
      }
      if (data.excluded_symptoms) {
        setExcludedSymptoms(data.excluded_symptoms)
      }
      if (data.patient_info && Object.keys(data.patient_info).length > 0) {
        setPatientInfo(data.patient_info)
      }

      const msg: Message = {
        id: crypto.randomUUID(),
        role: 'assistant',
        text: data.reply,
        suggestions: data.suggestions || [],
        diagnoses: data.diagnoses || [],
        treatment: data.treatment || undefined,
        excluded_symptoms: data.excluded_symptoms || [],
      }
      setMessages(m => [...m, msg])
    } catch (err) {
      const isAbort = err instanceof Error && err.name === 'AbortError'
      if (!isAbort) {
        const msg = err instanceof Error ? err.message : 'No se pudo conectar con el servidor. Verifica tu conexión.'
        setMessages(m => [...m, { id: crypto.randomUUID(), role: 'assistant', text: msg }])
      }
    }
    setIsSending(false)
  }

  const handleSuggestion = (symptom: string) => {
    handleSend(symptom)
  }

  const handleSelectDiagnosis = async (disease: string) => {
    setSelectedDiagnosis(disease)
    handleSend(disease)
  }

  const toggleDiagnosisConfirmation = (disease: string) => {
    setDoctorReview(prev => {
      const confirmed = prev.confirmedDiagnoses.includes(disease)
        ? prev.confirmedDiagnoses.filter(d => d !== disease)
        : [...prev.confirmedDiagnoses, disease]
      const rejected = prev.rejectedDiagnoses.includes(disease)
        ? prev.rejectedDiagnoses.filter(d => d !== disease)
        : prev.rejectedDiagnoses
      return { ...prev, confirmedDiagnoses: confirmed, rejectedDiagnoses: rejected }
    })
  }

  const toggleDiagnosisRejection = (disease: string) => {
    setDoctorReview(prev => {
      const rejected = prev.rejectedDiagnoses.includes(disease)
        ? prev.rejectedDiagnoses.filter(d => d !== disease)
        : [...prev.rejectedDiagnoses, disease]
      const confirmed = prev.confirmedDiagnoses.includes(disease)
        ? prev.confirmedDiagnoses.filter(d => d !== disease)
        : prev.confirmedDiagnoses
      return { ...prev, confirmedDiagnoses: confirmed, rejectedDiagnoses: rejected }
    })
  }

  const addManualDiagnosis = (diseaseName: string, notes: string = '') => {
    setDoctorReview(prev => ({
      ...prev,
      manualDiagnoses: [
        ...prev.manualDiagnoses,
        { id: crypto.randomUUID(), disease_name: diseaseName, notes },
      ],
    }))
  }

  const removeManualDiagnosis = (id: string) => {
    setDoctorReview(prev => ({
      ...prev,
      manualDiagnoses: prev.manualDiagnoses.filter(d => d.id !== id),
    }))
  }

  const toggleMedicineSelection = (medicineName: string) => {
    setDoctorReview(prev => {
      const selected = prev.selectedMedicines.includes(medicineName)
        ? prev.selectedMedicines.filter(m => m !== medicineName)
        : [...prev.selectedMedicines, medicineName]
      return { ...prev, selectedMedicines: selected }
    })
  }

  const updateMedicineDose = (medicineName: string, newDose: string) => {
    setDoctorReview(prev => ({
      ...prev,
      modifiedDoses: { ...prev.modifiedDoses, [medicineName]: newDose },
    }))
  }

  const setDoctorNotes = (notes: string) => {
    setDoctorReview(prev => ({ ...prev, doctorNotes: notes }))
  }

  const resetDoctorReview = () => {
    setDoctorReview({ ...INITIAL_DOCTOR_REVIEW })
  }

  const generateReport = async () => {
    setIsGeneratingReport(true)
    try {
      const res = await apiFetch('/api/report', {
        method: 'POST',
        body: JSON.stringify({
          patient_info: patientInfo,
          symptoms: currentSymptoms,
          selected_diagnosis: selectedDiagnosis,
          doctor_review: doctorReview,
          session_id: sessionId,
          document_number: patientInfo.id_document || selectedDocument,
        }),
      })
      if (!res.ok) {
        throw new Error(await extractError(res, 'No se pudo generar el reporte.'))
      }
      const data = await res.json()
      setReportHtml(data.html_report)
      setPhase('report')
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Error al generar el reporte.'
      setMessages(m => [...m, { id: crypto.randomUUID(), role: 'assistant', text: msg }])
    }
    setIsGeneratingReport(false)
  }

  const resetAll = () => {
    setPhase('search')
    setPatientInfoMode('full')
    setFormStep(0)
    setReportHtml(null)
    setCurrentSymptoms([])
    setExcludedSymptoms([])
    setPatientInfo({})
    setSelectedDiagnosis(null)
    setSessionId(null)
    setSelectedDocument('')
    setLastSession(null)
    setSearchQuery('')
    setSearchResults([])
    setShowSearchResults(false)
    setMessages(INITIAL_MESSAGES)
    setDoctorReview({ ...INITIAL_DOCTOR_REVIEW })
  }

  const backToSymptoms = () => {
    setPhase('symptoms')
    setReportHtml(null)
  }

  const confidenceColor = (c: number) => {
    if (c >= 0.7) return '#22c55e'
    if (c >= 0.4) return '#eab308'
    return '#ef4444'
  }

  const severityColor = (s: string) => {
    switch (s) {
      case 'mild': return '#22c55e'
      case 'moderate': return '#eab308'
      case 'high': return '#f97316'
      case 'critical': return '#ef4444'
      default: return '#6b7280'
    }
  }

  return {
    user,
    logout,
    phase,
    patientInfoMode,
    messages,
    input,
    setInput,
    isSending,
    isGeneratingReport,
    currentSymptoms,
    excludedSymptoms,
    patientInfo,
    reportHtml,
    formStep,
    setFormStep,
    selectedDiagnosis,
    lastSession,
    searchQuery,
    searchResults,
    showSearchResults,
    setShowSearchResults,
    searching,
    searchRef,
    endRef,
    sectionRefs,
    fieldGroups,
    allFieldKeys,
    sessionFieldKeys,
    suggestedSymptoms: messages
      .flatMap(m => m.suggestions || [])
      .filter((s, i, arr) => arr.indexOf(s) === i),
    doctorReview,
    handleSearchChange,
    selectPatient,
    startNewPatient,
    openHistory,
    resumeConsultation,
    startConsultationFromHistory,
    handlePatientFieldChange,
    submitPatientForm,
    handleSend,
    handleSuggestion,
    handleSelectDiagnosis,
    toggleDiagnosisConfirmation,
    toggleDiagnosisRejection,
    addManualDiagnosis,
    removeManualDiagnosis,
    toggleMedicineSelection,
    updateMedicineDose,
    setDoctorNotes,
    resetDoctorReview,
    generateReport,
    resetAll,
    backToSymptoms,
    confidenceColor,
    severityColor,
  }
}