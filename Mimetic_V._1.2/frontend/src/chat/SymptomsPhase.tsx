import { useEffect, useRef, useState, type RefObject } from 'react'
import type {
  Diagnosis,
  DoctorReview,
  Message,
  PatientInfo,
  SessionSnapshot,
  Treatment,
} from './types'
import AiWorkspace from './AiWorkspace'
import ClinicalShell from './ClinicalShell'
import PatientContextPanel from './PatientContextPanel'
import { Icon, useToast } from './ui'

type Props = {
  user: { name?: string } | null
  onLogout: () => void
  onHome: () => void
  onNewPatient: () => void
  onHistory: () => void
  onResume: () => void
  patientInfo: PatientInfo
  lastSession?: SessionSnapshot | null
  messages: Message[]
  input: string
  setInput: (v: string) => void
  isSending: boolean
  isGeneratingReport: boolean
  currentSymptoms: string[]
  excludedSymptoms: string[]
  suggestedSymptoms: string[]
  selectedDiagnosis: string | null
  doctorReview: DoctorReview
  endRef: RefObject<HTMLDivElement>
  onSend: (textOverride?: string) => void
  onSuggestion: (symptom: string) => void
  onSelectDiagnosis: (disease: string) => void
  onGenerateReport: () => void
  onToggleDiagnosisConfirmation: (disease: string) => void
  onToggleDiagnosisRejection: (disease: string) => void
  onAddManualDiagnosis: (diseaseName: string, notes?: string) => void
  onRemoveManualDiagnosis: (id: string) => void
  onToggleMedicine: (medicineName: string) => void
  onUpdateDose: (medicineName: string, newDose: string) => void
  onSetDoctorNotes: (notes: string) => void
  confidenceColor: (c: number) => string
  severityColor: (s: string) => string
}

const SEVERITY_LABEL: Record<string, string> = {
  mild: 'Leve',
  moderate: 'Moderado',
  high: 'Alto',
  critical: 'Crítico',
}

function DiagnosisCard({
  d,
  selected,
  onSelect,
  confidenceColor,
  severityColor,
  confirmed,
  rejected,
  onConfirm,
  onReject,
}: {
  d: Diagnosis
  selected: boolean
  onSelect: (disease: string) => void
  confidenceColor: (c: number) => string
  severityColor: (s: string) => string
  confirmed: boolean
  rejected: boolean
  onConfirm: (disease: string) => void
  onReject: (disease: string) => void
}) {
  const confidence = Math.round(d.confidence * 100)
  return (
    <div
      className={`rounded-xl border p-2.5 transition-all ${
        rejected
          ? 'border-slate-200 bg-slate-50 opacity-70'
          : confirmed
            ? 'border-emerald-300 bg-emerald-50/60 shadow-sm'
            : selected
              ? 'border-sky-300 bg-sky-50/60 shadow-sm'
              : 'border-surface-border bg-white hover:border-sky-200'
      }`}
    >
      <div className="flex items-start justify-between gap-2">
        <div className="flex min-w-0 items-start gap-2">
          <input
            type="checkbox"
            className="mt-0.5 h-3.5 w-3.5 flex-shrink-0 rounded"
            checked={confirmed}
            onClick={event => event.stopPropagation()}
            onChange={() => onConfirm(d.disease_name)}
            title="Confirmar diagnóstico"
            aria-label={`Confirmar ${d.disease_name}`}
          />
          <button
            type="button"
            onClick={() => onSelect(d.disease_name)}
            className="text-left text-[12px] font-bold text-text-primary hover:text-sky-700"
          >
            {d.disease_name}
          </button>
        </div>
        <span
          className="flex-shrink-0 rounded-full px-2 py-0.5 text-[10px] font-black"
          style={{ color: confidenceColor(d.confidence), backgroundColor: `${confidenceColor(d.confidence)}18` }}
        >
          {confidence}%
        </span>
      </div>

      <p className="mt-1 text-[10.5px] leading-snug text-text-secondary">{d.description}</p>

      <div className="mt-1.5 flex flex-wrap items-center gap-1">
        <span
          className="rounded px-1.5 py-0.5 text-[8.5px] font-bold uppercase tracking-wide text-white"
          style={{ background: severityColor(d.severity) }}
        >
          {SEVERITY_LABEL[d.severity] ?? d.severity}
        </span>
        <span className="rounded bg-surface-subtle px-1.5 py-0.5 font-code-telemetry text-[8.5px] font-semibold text-text-secondary">
          {d.matched_symptoms}/{d.total_input_symptoms} síntomas
        </span>
        {confirmed && (
          <span className="rounded border border-emerald-200 bg-emerald-100 px-1.5 py-0.5 text-[8.5px] font-bold text-emerald-700">
            confirmado
          </span>
        )}
        {rejected && (
          <span className="rounded border border-slate-200 bg-slate-100 px-1.5 py-0.5 text-[8.5px] font-bold text-slate-500">
            descartado
          </span>
        )}
      </div>

      {d.present_symptoms && d.present_symptoms.length > 0 && (
        <div className="mt-1.5 flex flex-wrap items-center gap-1">
          <span className="text-[8.5px] font-bold uppercase tracking-wider text-emerald-600">Presentes</span>
          {d.present_symptoms.map(symptom => (
            <span
              key={symptom}
              className="rounded-full border border-emerald-100 bg-emerald-50 px-1.5 py-0.5 text-[9px] text-emerald-700"
            >
              {symptom}
            </span>
          ))}
        </div>
      )}

      {d.missing_key_symptoms && d.missing_key_symptoms.length > 0 && (
        <div className="mt-1 flex flex-wrap items-center gap-1">
          <span className="text-[8.5px] font-bold uppercase tracking-wider text-amber-600">Faltan</span>
          {d.missing_key_symptoms.map(symptom => (
            <button
              key={symptom}
              type="button"
              onClick={() => onSelect(symptom)}
              className="rounded-full border border-amber-200 border-dashed bg-amber-50 px-1.5 py-0.5 text-[9px] text-amber-700 hover:bg-amber-100"
              title="Enviar este síntoma al motor"
            >
              + {symptom}
            </button>
          ))}
        </div>
      )}

      <div className="mt-1.5 flex items-center justify-end">
        <button
          type="button"
          onClick={event => {
            event.stopPropagation()
            onReject(d.disease_name)
          }}
          className={`rounded-lg border px-2 py-0.5 text-[9px] font-semibold transition-colors ${
            rejected
              ? 'border-slate-300 bg-slate-200 text-slate-700'
              : 'border-surface-border bg-white text-text-secondary hover:border-rose-200 hover:bg-rose-50 hover:text-rose-700'
          }`}
        >
          {rejected ? '✓ Descartado' : 'Descartar'}
        </button>
      </div>
    </div>
  )
}

function TreatmentBlock({
  treatment,
  doctorReview,
  onToggleMedicine,
  onUpdateDose,
}: {
  treatment: Treatment
  doctorReview: DoctorReview
  onToggleMedicine: (medicineName: string) => void
  onUpdateDose: (medicineName: string, newDose: string) => void
}) {
  const medicines = treatment.available && treatment.available.length > 0
    ? treatment.available
    : treatment.medicines || []
  const isSelected = (name: string) => doctorReview.selectedMedicines.includes(name)

  const renderDoseCell = (medicine: Treatment['medicines'] extends (infer M)[] | undefined ? M : never) => {
    const med = medicine as NonNullable<Treatment['medicines']>[number]
    return (
      <td>
        <span className="font-semibold text-text-primary">
          {med.calculated_dosage ? med.calculated_dosage : med.dosage}
        </span>
        {med.max_daily_dose && <div className="text-[9px] text-text-muted">Máx: {med.max_daily_dose}</div>}
        {med.dosage_mg_kg && <div className="font-code-telemetry text-[9px] text-text-muted">{med.dosage_mg_kg}</div>}
        <input
          className="mt-1 w-full min-w-[6rem] rounded border border-surface-border bg-surface-subtle px-1.5 py-0.5 text-[9.5px] outline-none focus:border-sky-300 focus:bg-white"
          value={doctorReview.modifiedDoses[med.name] ?? ''}
          placeholder="Ajustar dosis…"
          onChange={event => onUpdateDose(med.name, event.target.value)}
          aria-label={`Ajustar dosis de ${med.name}`}
        />
      </td>
    )
  }

  return (
    <div className="mt-2.5 rounded-xl border border-surface-border bg-white p-2.5">
      <h4 className="flex items-center gap-1.5 text-[10.5px] font-bold text-text-primary">
        <Icon name="medication" className="text-[15px] text-emerald-600" />
        Tratamiento sugerido · {treatment.disease_name}
      </h4>

      {medicines.length > 0 && (
        <>
          <h5 className="mt-2 text-[9px] font-bold uppercase tracking-wider text-text-muted">
            Medicamentos recomendados
          </h5>
          <div className="mt-1 overflow-x-auto rounded-lg border border-surface-border">
            <table className="mimetic-table min-w-[44rem]">
              <thead>
                <tr>
                  <th>Incluir</th>
                  <th>Medicamento</th>
                  <th>Dosis</th>
                  <th>Vía</th>
                  <th>Frecuencia</th>
                  <th>Duración</th>
                  <th>Monitoreo</th>
                </tr>
              </thead>
              <tbody>
                {medicines.map((medicine, index) => (
                  <tr key={`${medicine.name}-${index}`} className={isSelected(medicine.name) ? 'bg-emerald-50/40' : ''}>
                    <td>
                      <input
                        type="checkbox"
                        checked={isSelected(medicine.name)}
                        onChange={() => onToggleMedicine(medicine.name)}
                        title="Incluir en receta"
                        aria-label={`Incluir ${medicine.name}`}
                      />
                    </td>
                    <td className="min-w-[10rem]">
                      <strong className="text-[11px] text-text-primary">{medicine.name}</strong>
                      {medicine.reasons && medicine.reasons.length > 0 && (
                        <div className="mt-0.5 text-[9px] leading-snug text-amber-700">
                          {medicine.reasons.join('; ')}
                        </div>
                      )}
                      {medicine.patient_summary && (
                        <div className="mt-0.5 text-[9px] leading-snug text-text-muted">
                          {medicine.patient_summary}
                        </div>
                      )}
                    </td>
                    {renderDoseCell(medicine)}
                    <td>{medicine.route || 'Oral'}</td>
                    <td>{medicine.frequency}</td>
                    <td>{medicine.duration}</td>
                    <td>{medicine.monitoring || '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}

      {treatment.available && treatment.available.length > 0 && treatment.available.some(medicine => medicine.adjustments) && (
        <div className="mt-2 flex flex-col gap-1">
          {treatment.available.map((medicine, index) =>
            medicine.adjustments && Object.values(medicine.adjustments).some(Boolean) ? (
              <details key={`${medicine.name}-${index}`} className="rounded-lg border border-surface-border bg-surface-subtle/60 px-2 py-1.5">
                <summary className="cursor-pointer text-[9.5px] font-bold text-text-secondary">
                  Ajustes para {medicine.name}
                </summary>
                <div className="mt-1 space-y-0.5 text-[9.5px] leading-snug text-text-secondary">
                  {medicine.adjustments.renal && <p><strong>Renal:</strong> {medicine.adjustments.renal}</p>}
                  {medicine.adjustments.hepatic && <p><strong>Hepático:</strong> {medicine.adjustments.hepatic}</p>}
                  {medicine.adjustments.pediatric && <p><strong>Pediátrico:</strong> {medicine.adjustments.pediatric}</p>}
                  {medicine.adjustments.geriatric && <p><strong>Geriatría:</strong> {medicine.adjustments.geriatric}</p>}
                  {medicine.adjustments.pregnancy && <p><strong>Embarazo:</strong> {medicine.adjustments.pregnancy}</p>}
                  {medicine.interactions_warning && (
                    <p className="text-amber-700"><strong>Interacciones:</strong> {medicine.interactions_warning}</p>
                  )}
                  {medicine.contraindications &&
                    (medicine.contraindications.conditions?.length > 0 ||
                      medicine.contraindications.allergies?.length > 0) && (
                      <p className="text-rose-700">
                        <strong>Contraindicaciones:</strong>{' '}
                        {[
                          ...(medicine.contraindications.conditions || []),
                          ...(medicine.contraindications.allergies || []),
                        ].join(', ')}
                      </p>
                    )}
                </div>
              </details>
            ) : null,
          )}
        </div>
      )}

      {treatment.not_recommended && treatment.not_recommended.length > 0 && (
        <div className="mt-2">
          <h5 className="text-[9px] font-bold uppercase tracking-wider text-rose-600">No recomendados</h5>
          <div className="mt-1 flex flex-col gap-1">
            {treatment.not_recommended.map((medicine, index) => (
              <div key={`${medicine.name}-${index}`} className="rounded-lg border border-rose-100 bg-rose-50 px-2 py-1 text-[9.5px] text-rose-800">
                <strong>{medicine.name}</strong> — {medicine.reasons?.join(', ') || 'Contraindicado'}
                {medicine.patient_summary && <div className="text-[9px] text-rose-600">{medicine.patient_summary}</div>}
              </div>
            ))}
          </div>
        </div>
      )}

      {treatment.alternatives && treatment.alternatives.length > 0 && (
        <div className="mt-2">
          <h5 className="text-[9px] font-bold uppercase tracking-wider text-text-muted">Alternativas</h5>
          <div className="mt-1 overflow-x-auto rounded-lg border border-surface-border">
            <table className="mimetic-table min-w-[34rem]">
              <thead>
                <tr>
                  <th>Incluir</th>
                  <th>Alternativa</th>
                  <th>Dosis</th>
                  <th>Vía</th>
                  <th>Frecuencia</th>
                  <th>Duración</th>
                </tr>
              </thead>
              <tbody>
                {treatment.alternatives.map((medicine, index) => (
                  <tr key={`${medicine.name}-${index}`} className={isSelected(medicine.name) ? 'bg-emerald-50/40' : ''}>
                    <td>
                      <input
                        type="checkbox"
                        checked={isSelected(medicine.name)}
                        onChange={() => onToggleMedicine(medicine.name)}
                        aria-label={`Incluir ${medicine.name}`}
                      />
                    </td>
                    <td>
                      <strong className="text-[11px] text-text-primary">{medicine.name}</strong>
                      {medicine.patient_summary && (
                        <div className="text-[9px] text-text-muted">{medicine.patient_summary}</div>
                      )}
                    </td>
                    {renderDoseCell(medicine)}
                    <td>{medicine.route || 'Oral'}</td>
                    <td>{medicine.frequency}</td>
                    <td>{medicine.duration}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {treatment.non_pharmacological && treatment.non_pharmacological.length > 0 && (
        <div className="mt-2">
          <h5 className="text-[9px] font-bold uppercase tracking-wider text-text-muted">
            Medidas no farmacológicas
          </h5>
          <ul className="mt-1 list-inside list-disc space-y-0.5 text-[9.5px] text-text-secondary">
            {treatment.non_pharmacological.map((recommendation, index) => (
              <li key={index}>{recommendation}</li>
            ))}
          </ul>
        </div>
      )}

      {treatment.general_recommendations && (
        <div className="mt-2 rounded-lg border border-sky-100 bg-sky-50/70 px-2 py-1.5 text-[9.5px] leading-snug text-sky-900">
          <strong>Recomendaciones:</strong> {treatment.general_recommendations}
        </div>
      )}
    </div>
  )
}

function MessageBubble({
  msg,
  doctorName,
  selectedDiagnosis,
  onSuggestion,
  onSelectDiagnosis,
  confidenceColor,
  severityColor,
  doctorReview,
  onToggleDiagnosisConfirmation,
  onToggleDiagnosisRejection,
  onToggleMedicine,
  onUpdateDose,
}: {
  msg: Message
  doctorName: string
  selectedDiagnosis: string | null
  onSuggestion: (symptom: string) => void
  onSelectDiagnosis: (disease: string) => void
  confidenceColor: (c: number) => string
  severityColor: (s: string) => string
  doctorReview: DoctorReview
  onToggleDiagnosisConfirmation: (disease: string) => void
  onToggleDiagnosisRejection: (disease: string) => void
  onToggleMedicine: (medicineName: string) => void
  onUpdateDose: (medicineName: string, newDose: string) => void
}) {
  const isUser = msg.role === 'user'

  return (
    <div className={`flex items-start gap-2.5 ${isUser ? 'flex-row-reverse pl-6' : 'pr-1'}`}>
      <div
        className={`mt-0.5 flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-xl text-[10px] font-bold shadow-sm ${
          isUser
            ? 'bg-gradient-to-tr from-clinical-primary to-sky-600 text-white'
            : 'border border-sky-200 bg-sky-100 text-sky-700'
        }`}
        title={isUser ? doctorName : 'Mimetic Medical Engine'}
      >
        {isUser ? doctorName.split(' ').slice(-2).map(part => part[0]).join('').slice(0, 2).toUpperCase() : <Icon name="psychology" className="text-[18px]" />}
      </div>

      <div className={`flex w-full max-w-[94%] flex-col gap-1 ${isUser ? 'items-end' : 'items-start'}`}>
        <div className={`flex flex-wrap items-center gap-1.5 text-[9.5px] ${isUser ? 'flex-row-reverse' : ''}`}>
          <span className="font-bold text-text-primary">{isUser ? doctorName : 'Mimetic Diagnostic Engine'}</span>
          {!isUser && (
            <span className="rounded-full border border-sky-200 bg-sky-50 px-1.5 py-0.5 text-[8px] font-bold text-sky-700">
              Actualizado
            </span>
          )}
          <span className="text-text-muted">ahora</span>
        </div>

        <div
          className={`w-full rounded-2xl border p-2.5 text-[11.5px] leading-relaxed shadow-sm ${
            isUser
              ? 'rounded-tr-sm border-clinical-primary bg-clinical-primary text-white'
              : 'rounded-tl-sm border-surface-border bg-white text-text-secondary'
          }`}
        >
          <p className="whitespace-pre-wrap">{msg.text}</p>

          {msg.suggestions && msg.suggestions.length > 0 && (
            <div className="mt-2">
              <span className="text-[8.5px] font-bold uppercase tracking-wider text-sky-700">
                Sugerencias
              </span>
              <div className="mt-1 flex flex-wrap gap-1">
                {msg.suggestions.map(symptom => (
                  <button
                    key={symptom}
                    type="button"
                    onClick={() => onSuggestion(symptom)}
                    className="rounded-full border border-sky-200 bg-sky-50 px-2 py-0.5 text-[9.5px] font-semibold text-sky-800 transition-colors hover:bg-sky-100"
                  >
                    + {symptom}
                  </button>
                ))}
              </div>
            </div>
          )}

          {msg.diagnoses && msg.diagnoses.length > 0 && (
            <div className="mt-2">
              <div className="mb-1 flex items-center justify-between gap-2">
                <span className="text-[9px] font-bold uppercase tracking-wider text-text-secondary">
                  Diagnósticos diferenciales
                </span>
                <span className="text-[8.5px] text-text-muted">Marca los que confirmas</span>
              </div>
              <div className="flex flex-col gap-1.5">
                {msg.diagnoses.map(diagnosis => (
                  <DiagnosisCard
                    key={diagnosis.disease_name}
                    d={diagnosis}
                    selected={selectedDiagnosis === diagnosis.disease_name}
                    onSelect={onSelectDiagnosis}
                    confidenceColor={confidenceColor}
                    severityColor={severityColor}
                    confirmed={doctorReview.confirmedDiagnoses.includes(diagnosis.disease_name)}
                    rejected={doctorReview.rejectedDiagnoses.includes(diagnosis.disease_name)}
                    onConfirm={onToggleDiagnosisConfirmation}
                    onReject={onToggleDiagnosisRejection}
                  />
                ))}
              </div>
              <p className="mt-1 text-[8.5px] text-text-muted">
                Haz clic en el nombre para ver el tratamiento sugerido.
              </p>
            </div>
          )}

          {msg.treatment && (
            <TreatmentBlock
              treatment={msg.treatment}
              doctorReview={doctorReview}
              onToggleMedicine={onToggleMedicine}
              onUpdateDose={onUpdateDose}
            />
          )}
        </div>
      </div>
    </div>
  )
}

export default function SymptomsPhase({
  user,
  onLogout,
  onHome,
  onNewPatient,
  onHistory,
  onResume,
  patientInfo,
  lastSession,
  messages,
  input,
  setInput,
  isSending,
  isGeneratingReport,
  currentSymptoms,
  excludedSymptoms,
  suggestedSymptoms,
  selectedDiagnosis,
  doctorReview,
  endRef,
  onSend,
  onSuggestion,
  onSelectDiagnosis,
  onGenerateReport,
  onToggleDiagnosisConfirmation,
  onToggleDiagnosisRejection,
  onAddManualDiagnosis,
  onRemoveManualDiagnosis,
  onToggleMedicine,
  onUpdateDose,
  onSetDoctorNotes,
  confidenceColor,
  severityColor,
}: Props) {
  const showToast = useToast()
  const [manualDiagInput, setManualDiagInput] = useState('')
  const [dictating, setDictating] = useState(false)
  const [handsFree, setHandsFree] = useState(false)
  const dictationTimer = useRef<ReturnType<typeof setTimeout> | null>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  const doctorName = user?.name || 'Médico tratante'
  const patientLabel =
    patientInfo.name || `${patientInfo.first_name ?? ''} ${patientInfo.last_name ?? ''}`.trim() || 'Paciente'
  const hasConfirmedDiagnosis =
    doctorReview.confirmedDiagnoses.length > 0 || doctorReview.manualDiagnoses.length > 0
  const totalConfirmed = doctorReview.confirmedDiagnoses.length + doctorReview.manualDiagnoses.length

  useEffect(() => {
    return () => {
      if (dictationTimer.current) clearTimeout(dictationTimer.current)
    }
  }, [])

  const handleAddManualDiagnosis = () => {
    if (manualDiagInput.trim()) {
      onAddManualDiagnosis(manualDiagInput.trim())
      setManualDiagInput('')
    }
  }

  const handleDictation = () => {
    if (dictating) {
      if (dictationTimer.current) clearTimeout(dictationTimer.current)
      setDictating(false)
      showToast('Dictado simulado cancelado.', { icon: 'mic_off', tone: 'info' })
      return
    }
    setDictating(true)
    showToast('Dictado simulado en curso… no se graba audio real.', { icon: 'mic', tone: 'info' })
    dictationTimer.current = setTimeout(() => {
      setDictating(false)
      setInput(
        'Auscultación pulmonar: murmullo vesicular disminuido y estertores crepitantes inspiratorios en base hemitorácica derecha. Frecuencia respiratoria 22 rpm.',
      )
      inputRef.current?.focus()
      showToast('Transcripción simulada lista. Revísala antes de enviarla.', {
        icon: 'graphic_eq',
        tone: 'warn',
      })
    }, 1900)
  }

  const handleCommand = (command: string) => {
    if (command === 'listo') {
      onSend('listo')
      return
    }
    if (command === 'triaje') {
      showToast('El triaje Manchester/ESI se registra en el formulario de la sesión y se muestra en el panel del paciente.', {
        icon: 'emergency',
        tone: 'info',
      })
      return
    }
    if (command === 'labs') {
      showToast('El laboratorio urgente se registra en el paso «Laboratorio urgente» del formulario.', {
        icon: 'science',
        tone: 'info',
      })
      return
    }
    showToast('Bundle FHIR R4: vista simulada en la pestaña FHIR del panel del paciente.', {
      icon: 'hub',
      tone: 'info',
    })
  }

  const sendMessage = () => {
    if (!input.trim() || isSending) return
    onSend()
  }

  return (
    <ClinicalShell
      user={user}
      onLogout={onLogout}
      phase="symptoms"
      onHome={onHome}
      onNewPatient={onNewPatient}
      onHistory={onHistory}
      onResume={onResume}
      breadcrumb={['Urgencias Hospital Central', 'Consultorio 04', patientLabel, 'Evaluación asistida']}
    >
      <div className="grid grid-cols-1 items-start gap-4 xl:grid-cols-12">
        {/* ── Contexto del paciente ────────────────────────────── */}
        <div className="xl:col-span-5">
          <PatientContextPanel
            patientInfo={patientInfo}
            lastSession={lastSession}
            currentSymptoms={currentSymptoms}
            doctorReview={doctorReview}
          />
        </div>

        {/* ── Motor de diagnóstico ─────────────────────────────── */}
        <div className="flex min-w-0 flex-col gap-4 xl:col-span-7">
          <AiWorkspace
            title="Mimetic Medical Engine"
            subtitle="Ontología SNOMED-CT / CIE-11 · inferencia bayesiana local"
            badge="v4.2 PRO"
            icon="smart_toy"
            status={
              <span className="hidden items-center gap-1 rounded border border-emerald-200 bg-emerald-50 px-1.5 py-0.5 font-code-telemetry text-[9px] font-bold text-emerald-700 sm:flex">
                <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-emerald-500" />
                motor local
              </span>
            }
            actions={
              <>
                <button
                  type="button"
                  onClick={() => {
                    setHandsFree(value => !value)
                    showToast(
                      handsFree
                        ? 'Modo manos libres pausado.'
                        : 'Modo manos libres simulado: no se captura audio real.',
                      { icon: handsFree ? 'pause' : 'mic', tone: 'info' },
                    )
                  }}
                  className={`flex items-center gap-1.5 rounded-lg border px-2 py-1 text-[9.5px] font-bold transition-colors ${
                    handsFree
                      ? 'border-sky-300 bg-sky-100 text-sky-800'
                      : 'border-surface-border bg-white text-text-secondary hover:bg-surface-subtle'
                  }`}
                  title="Modo manos libres (simulado)"
                >
                  <span className="relative flex h-2 w-2">
                    {handsFree && <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-sky-400 opacity-70" />}
                    <span className={`relative inline-flex h-2 w-2 rounded-full ${handsFree ? 'bg-sky-600' : 'bg-slate-400'}`} />
                  </span>
                  <span className="hidden sm:inline">{handsFree ? 'Manos libres' : 'Manos libres'}</span>
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setInput('')
                    showToast('Entrada limpiada. El historial de la conversación se conserva.', {
                      icon: 'backspace',
                      tone: 'info',
                    })
                  }}
                  className="rounded-lg border border-surface-border p-1.5 text-text-muted transition-colors hover:bg-surface-subtle hover:text-text-primary"
                  title="Limpiar entrada"
                  aria-label="Limpiar entrada"
                >
                  <Icon name="backspace" className="text-[17px]" />
                </button>
              </>
            }
            className="h-[68vh] min-h-[32rem] xl:h-[calc(100vh-9.5rem)] xl:min-h-[40rem]"
            bodyClassName="flex flex-col"
          >
            {/* Conversación */}
            <div className="flex-1 space-y-3 overflow-y-auto bg-surface-canvas/60 p-3">
              {messages.map(message => (
                <MessageBubble
                  key={message.id}
                  msg={message}
                  doctorName={doctorName}
                  selectedDiagnosis={selectedDiagnosis}
                  onSuggestion={onSuggestion}
                  onSelectDiagnosis={onSelectDiagnosis}
                  confidenceColor={confidenceColor}
                  severityColor={severityColor}
                  doctorReview={doctorReview}
                  onToggleDiagnosisConfirmation={onToggleDiagnosisConfirmation}
                  onToggleDiagnosisRejection={onToggleDiagnosisRejection}
                  onToggleMedicine={onToggleMedicine}
                  onUpdateDose={onUpdateDose}
                />
              ))}

              {isSending && (
                <div className="flex items-start gap-2.5">
                  <div className="mt-0.5 flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-xl border border-sky-200 bg-sky-100 text-sky-700">
                    <Icon name="psychology" className="text-[18px]" />
                  </div>
                  <div className="flex items-center gap-1 rounded-2xl rounded-tl-sm border border-surface-border bg-white px-3 py-2.5 shadow-sm">
                    {[0, 1, 2].map(index => (
                      <span
                        key={index}
                        className="h-1.5 w-1.5 animate-bounce rounded-full bg-sky-400"
                        style={{ animationDelay: `${index * 0.12}s` }}
                      />
                    ))}
                    <span className="ml-1.5 text-[9.5px] font-semibold text-text-muted">
                      Correlacionando síntomas…
                    </span>
                  </div>
                </div>
              )}

              <div ref={endRef} />
            </div>

            {/* Compositor */}
            <div className="border-t border-surface-border bg-white p-2.5">
              {currentSymptoms.length > 0 && !isSending && (
                <div className="mb-2 flex flex-wrap items-center gap-1">
                  <span className="flex items-center gap-0.5 text-[8.5px] font-bold uppercase tracking-wider text-text-muted">
                    <Icon name="bolt" className="text-[12px] text-amber-500" filled />
                    Rápido
                  </span>
                  {suggestedSymptoms.slice(0, 4).map(symptom => (
                    <button
                      key={symptom}
                      type="button"
                      onClick={() => onSuggestion(symptom)}
                      className="rounded-full border border-sky-200 bg-sky-50 px-2 py-0.5 text-[9.5px] font-semibold text-sky-800 transition-colors hover:bg-sky-100"
                    >
                      + {symptom}
                    </button>
                  ))}
                  <button
                    type="button"
                    onClick={() => onSend('listo')}
                    className="rounded-full border border-emerald-200 bg-emerald-50 px-2 py-0.5 text-[9.5px] font-bold text-emerald-700 transition-colors hover:bg-emerald-100"
                  >
                    Ver diagnósticos
                  </button>
                </div>
              )}

              {excludedSymptoms.length > 0 && (
                <div className="mb-2 flex flex-wrap items-center gap-1">
                  <span className="text-[8.5px] font-bold uppercase tracking-wider text-rose-600">
                    Descartados
                  </span>
                  {excludedSymptoms.map(symptom => (
                    <span
                      key={symptom}
                      className="rounded-full border border-rose-200 bg-rose-50 px-2 py-0.5 text-[9px] text-rose-700 line-through"
                    >
                      {symptom}
                    </span>
                  ))}
                </div>
              )}

              <div className="rounded-xl border border-surface-border bg-surface-subtle/50 p-1.5">
                <div className="flex items-end gap-1.5">
                  <button
                    type="button"
                    onClick={handleDictation}
                    className={`flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-lg bg-gradient-to-tr from-clinical-primary to-sky-600 text-white shadow-sm transition-all hover:brightness-110 ${
                      dictating ? 'ring-4 ring-rose-200' : ''
                    }`}
                    title="Dictado clínico (simulado)"
                    aria-label="Dictado clínico simulado"
                  >
                    <Icon name={dictating ? 'stop' : 'mic'} className="text-[18px]" />
                  </button>

                  <textarea
                    ref={inputRef}
                    rows={2}
                    value={input}
                    onChange={event => setInput(event.target.value)}
                    onKeyDown={event => {
                      if (event.key === 'Enter' && !event.shiftKey) {
                        event.preventDefault()
                        sendMessage()
                      }
                    }}
                    placeholder="Describe síntomas, dicta hallazgos o consulta posología…"
                    disabled={isSending}
                    className="max-h-24 min-h-[2.5rem] flex-1 resize-none rounded-lg border-0 bg-white px-2.5 py-1.5 text-[11.5px] leading-relaxed text-text-primary outline-none placeholder:text-slate-400 focus:ring-2 focus:ring-sky-100 disabled:opacity-60"
                  />

                  <div className="flex flex-shrink-0 flex-col items-center gap-1">
                    <button
                      type="button"
                      onClick={() =>
                        showToast('Carga de imagen DICOM o laboratorio: simulación, no se envía archivo.', {
                          icon: 'upload_file',
                          tone: 'info',
                        })
                      }
                      className="rounded-lg p-1.5 text-text-muted transition-colors hover:bg-white hover:text-text-primary"
                      title="Adjuntar imagen o laboratorio (simulado)"
                    >
                      <Icon name="attach_file" className="text-[17px]" />
                    </button>
                    <button
                      type="button"
                      onClick={sendMessage}
                      disabled={isSending || !input.trim()}
                      className="flex h-9 w-9 items-center justify-center rounded-lg bg-clinical-primary text-white shadow-sm transition-all hover:bg-[#072a4a] active:scale-95 disabled:opacity-40"
                      title="Enviar (Enter)"
                      aria-label="Enviar mensaje"
                    >
                      <Icon name="send" className="text-[18px]" />
                    </button>
                  </div>
                </div>

                <div className="mt-1 flex flex-wrap items-center justify-between gap-1 px-0.5">
                  <div className="flex flex-wrap items-center gap-1">
                    {[
                      { id: 'triaje', label: '/triaje', icon: 'emergency', tone: 'amber' },
                      { id: 'labs', label: '/lab', icon: 'science', tone: 'violet' },
                      { id: 'fhir', label: '/fhir', icon: 'hub', tone: 'sky' },
                      { id: 'listo', label: '/listo', icon: 'playlist_add_check', tone: 'emerald' },
                    ].map(command => (
                      <button
                        key={command.id}
                        type="button"
                        onClick={() => handleCommand(command.id)}
                        className={`flex items-center gap-0.5 rounded-full border px-2 py-0.5 font-code-telemetry text-[9px] font-bold transition-colors ${
                          command.tone === 'amber'
                            ? 'border-amber-200 bg-amber-50 text-amber-800 hover:bg-amber-100'
                            : command.tone === 'violet'
                              ? 'border-violet-200 bg-violet-50 text-violet-800 hover:bg-violet-100'
                              : command.tone === 'sky'
                                ? 'border-sky-200 bg-sky-50 text-sky-800 hover:bg-sky-100'
                                : 'border-emerald-200 bg-emerald-50 text-emerald-800 hover:bg-emerald-100'
                        }`}
                      >
                        <Icon name={command.icon} className="text-[11px]" />
                        {command.label}
                      </button>
                    ))}
                  </div>
                  <span className="flex items-center gap-1 font-code-telemetry text-[8.5px] text-text-muted">
                    <Icon name="keyboard" className="text-[12px]" />
                    Enter envía · Shift+Enter salto
                  </span>
                </div>
              </div>

              <div className="mt-1 flex flex-wrap items-center justify-between gap-1 px-1 text-[8.5px] text-text-muted">
                <span className="flex items-center gap-1">
                  <span className={`h-1.5 w-1.5 rounded-full ${isSending ? 'animate-pulse bg-amber-500' : 'bg-emerald-500'}`} />
                  {isSending ? 'Procesando con el motor clínico…' : 'Motor listo · sin captura de audio real'}
                </span>
                <span className="font-code-telemetry">
                  {currentSymptoms.length} síntoma(s) normalizado(s)
                </span>
              </div>
            </div>
          </AiWorkspace>

          {/* ── Revisión y cierre ──────────────────────────────── */}
          <section className="rounded-2xl border border-surface-border bg-white p-3.5 shadow-sm">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <h2 className="flex items-center gap-1.5 font-headline-sm text-[13px] font-bold text-text-primary">
                <Icon name="fact_check" className="text-[18px] text-sky-600" />
                Revisión y cierre médico
              </h2>
              <div className="flex items-center gap-1.5">
                <span className="rounded-full border border-emerald-200 bg-emerald-50 px-2 py-0.5 text-[9.5px] font-bold text-emerald-700">
                  {totalConfirmed} confirmado(s)
                </span>
                {doctorReview.rejectedDiagnoses.length > 0 && (
                  <span className="rounded-full border border-slate-200 bg-slate-100 px-2 py-0.5 text-[9.5px] font-bold text-slate-500">
                    {doctorReview.rejectedDiagnoses.length} descartado(s)
                  </span>
                )}
              </div>
            </div>

            <div className="mt-2.5 grid grid-cols-1 gap-3 lg:grid-cols-2">
              <div className="flex flex-col gap-2">
                <label className="text-[9.5px] font-bold uppercase tracking-wider text-text-muted">
                  Diagnóstico manual del médico
                </label>
                <div className="flex items-center gap-1.5">
                  <input
                    value={manualDiagInput}
                    onChange={event => setManualDiagInput(event.target.value)}
                    onKeyDown={event => event.key === 'Enter' && handleAddManualDiagnosis()}
                    placeholder="Agregar diagnóstico manual…"
                    className="min-w-0 flex-1 rounded-lg border border-transparent bg-surface-subtle px-2.5 py-1.5 text-[11px] text-text-primary outline-none transition-all placeholder:text-slate-400 focus:border-sky-200 focus:bg-white focus:ring-2 focus:ring-sky-100"
                  />
                  <button
                    type="button"
                    onClick={handleAddManualDiagnosis}
                    disabled={!manualDiagInput.trim()}
                    className="flex flex-shrink-0 items-center gap-1 rounded-lg bg-sky-600 px-2.5 py-1.5 text-[10.5px] font-bold text-white transition-colors hover:bg-sky-700 disabled:opacity-40"
                  >
                    <Icon name="add" className="text-[15px]" /> Agregar
                  </button>
                </div>

                {doctorReview.manualDiagnoses.length > 0 && (
                  <div className="flex flex-col gap-1">
                    {doctorReview.manualDiagnoses.map(diagnosis => (
                      <div
                        key={diagnosis.id}
                        className="flex items-center justify-between gap-1.5 rounded-lg border border-violet-100 bg-violet-50 px-2 py-1"
                      >
                        <span className="min-w-0">
                          <span className="block truncate text-[10.5px] font-semibold text-violet-900">
                            {diagnosis.disease_name}
                          </span>
                          {diagnosis.notes && <em className="block text-[9px] text-violet-600">{diagnosis.notes}</em>}
                        </span>
                        <button
                          type="button"
                          onClick={() => onRemoveManualDiagnosis(diagnosis.id)}
                          className="rounded p-0.5 text-violet-400 hover:bg-white hover:text-rose-600"
                          aria-label={`Quitar ${diagnosis.disease_name}`}
                        >
                          <Icon name="close" className="text-[14px]" />
                        </button>
                      </div>
                    ))}
                  </div>
                )}

                {doctorReview.confirmedDiagnoses.length > 0 && (
                  <div className="flex flex-wrap gap-1">
                    {doctorReview.confirmedDiagnoses.map(disease => (
                      <span
                        key={disease}
                        className="flex items-center gap-0.5 rounded-full border border-emerald-200 bg-emerald-50 px-1.5 py-0.5 text-[9px] font-semibold text-emerald-700"
                      >
                        <Icon name="check" className="text-[11px]" /> {disease}
                      </span>
                    ))}
                  </div>
                )}
              </div>

              <div className="flex flex-col gap-2">
                <label htmlFor="doctor-notes" className="text-[9.5px] font-bold uppercase tracking-wider text-text-muted">
                  Notas y ajustes del médico
                </label>
                <textarea
                  id="doctor-notes"
                  value={doctorReview.doctorNotes}
                  onChange={event => onSetDoctorNotes(event.target.value)}
                  placeholder="Observaciones, ajustes de dosis, recomendaciones específicas…"
                  rows={4}
                  className="w-full resize-none rounded-lg border border-transparent bg-surface-subtle px-2.5 py-1.5 text-[11px] leading-relaxed text-text-primary outline-none transition-all placeholder:text-slate-400 focus:border-sky-200 focus:bg-white focus:ring-2 focus:ring-sky-100"
                />
              </div>
            </div>

            <div className="mt-3 flex flex-wrap items-center justify-between gap-2 border-t border-surface-border pt-2.5">
              <p className="max-w-md text-[9.5px] leading-snug text-text-muted">
                {hasConfirmedDiagnosis
                  ? 'La historia clínica se genera con los diagnósticos confirmados, los medicamentos seleccionados y tus notas.'
                  : 'Confirma al menos un diagnóstico en el chat para habilitar la generación de la historia clínica.'}
              </p>
              <button
                type="button"
                onClick={onGenerateReport}
                disabled={!hasConfirmedDiagnosis || isGeneratingReport}
                className="flex items-center gap-1.5 rounded-xl bg-gradient-to-r from-clinical-primary to-sky-700 px-4 py-2.5 text-[11.5px] font-bold text-white shadow-md transition-all hover:brightness-110 active:scale-[0.99] disabled:cursor-not-allowed disabled:opacity-40"
              >
                <Icon
                  name={isGeneratingReport ? 'hourglass_top' : 'description'}
                  className={`text-[17px] ${isGeneratingReport ? 'animate-spin' : ''}`}
                />
                {isGeneratingReport ? 'Generando historia…' : 'Confirmar y generar historia clínica'}
              </button>
            </div>
          </section>
        </div>
      </div>
    </ClinicalShell>
  )
}
