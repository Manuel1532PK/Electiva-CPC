import { type MutableRefObject, type RefObject } from 'react'
import { SECTION_ICONS } from './constants'
import type { Message, PatientInfo, PatientInfoMode, SearchResult, SessionSnapshot } from './types'
import AiWorkspace from './AiWorkspace'
import ClinicalShell from './ClinicalShell'
import PatientContextPanel from './PatientContextPanel'
import { Icon } from './ui'

type FieldGroup = { title: string; fields: { key: string; label: string; placeholder?: string; type?: 'text' | 'select'; options?: { value: string; label: string }[]; suffix?: string; condition?: (info: PatientInfo) => boolean }[] }

export type SearchResultType = SearchResult

type Props = {
  user: { name?: string } | null
  onLogout: () => void
  onHome: () => void
  onNewPatient: () => void
  onHistory: () => void
  onResume: () => void
  patientInfoMode: PatientInfoMode
  patientInfo: PatientInfo
  lastSession?: SessionSnapshot | null
  formStep: number
  setFormStep: (updater: number | ((s: number) => number)) => void
  fieldGroups: FieldGroup[]
  allFieldKeys: string[]
  sessionFieldKeys: string[]
  sectionRefs: MutableRefObject<(HTMLDivElement | null)[]>
  messages: Message[]
  endRef: RefObject<HTMLDivElement>
  isSending: boolean
  onFieldChange: (key: string, value: string) => void
  onSubmit: () => void
}

function displayValue(field: FieldGroup['fields'][number], value: string) {
  if (field.type === 'select') {
    return field.options?.find(option => option.value === value)?.label ?? value
  }
  return value
}

export default function PatientInfoPhase({
  user,
  onLogout,
  onHome,
  onNewPatient,
  onHistory,
  onResume,
  patientInfoMode,
  patientInfo,
  lastSession,
  formStep,
  setFormStep,
  fieldGroups,
  allFieldKeys,
  sessionFieldKeys,
  sectionRefs,
  messages,
  endRef,
  isSending,
  onFieldChange,
  onSubmit,
}: Props) {
  const filledCount = Object.values(patientInfo).filter(value => value?.toString().trim()).length
  const totalKeys = patientInfoMode === 'full' ? allFieldKeys.length : sessionFieldKeys.length
  const progress = Math.min(100, Math.round((filledCount / Math.max(totalKeys, 1)) * 100))
  const visibleGroup = fieldGroups[formStep]
  const isLastStep = formStep === fieldGroups.length - 1
  const patientLabel =
    patientInfo.name || `${patientInfo.first_name ?? ''} ${patientInfo.last_name ?? ''}`.trim() || 'Paciente nuevo'

  const goNextField = (target: HTMLInputElement | HTMLSelectElement) => {
    const inputs = Array.from(document.querySelectorAll<HTMLElement>('.patient-field-input'))
    const current = inputs.indexOf(target)
    const next = inputs[current + 1]
    if (next) next.focus()
  }

  return (
    <ClinicalShell
      user={user}
      onLogout={onLogout}
      phase="patient_info"
      onHome={onHome}
      onNewPatient={onNewPatient}
      onHistory={onHistory}
      onResume={onResume}
      breadcrumb={['Admisión', patientLabel, patientInfoMode === 'session_only' ? 'Datos de la sesión' : 'Registro del paciente']}
    >
      <div className="grid grid-cols-1 items-start gap-4 xl:grid-cols-12">
        <div className="xl:col-span-5">
          <PatientContextPanel
            patientInfo={patientInfo}
            lastSession={lastSession}
            currentSymptoms={lastSession?.symptoms ?? []}
          />
        </div>

        <div className="xl:col-span-7">
          <AiWorkspace
            title={patientInfoMode === 'session_only' ? 'Datos de la consulta' : 'Registro del paciente'}
            subtitle="Anamnesis, antecedentes, signos vitales, triaje y laboratorio"
            badge={patientInfoMode === 'session_only' ? 'Paciente existente' : 'Nuevo ingreso'}
            icon="clinical_notes"
            status={
              <span className="rounded border border-emerald-200 bg-emerald-50 px-1.5 py-0.5 text-[9px] font-bold uppercase text-emerald-700">
                persistencia real
              </span>
            }
            actions={
              <span className="flex items-center gap-1 rounded-lg border border-sky-200 bg-sky-50 px-2 py-1 font-code-telemetry text-[10px] font-bold text-sky-800">
                <Icon name="autorenew" className="text-[14px]" />
                {progress}% completo
              </span>
            }
          >
            <div className="flex flex-col gap-4 p-3.5 sm:p-4">
              {/* Mensajes del asistente */}
              <div className="flex max-h-36 flex-col gap-2 overflow-y-auto rounded-xl border border-surface-border bg-surface-subtle/60 p-2.5">
                {messages.map(message => (
                  <div
                    key={message.id}
                    className={`flex items-start gap-2 ${message.role === 'user' ? 'flex-row-reverse' : ''}`}
                  >
                    <div
                      className={`flex h-6 w-6 flex-shrink-0 items-center justify-center rounded-lg text-[9px] font-bold ${
                        message.role === 'user'
                          ? 'bg-clinical-primary text-white'
                          : 'border border-sky-200 bg-sky-100 text-sky-700'
                      }`}
                    >
                      {message.role === 'user' ? 'MD' : <Icon name="psychology" className="text-[14px]" />}
                    </div>
                    <div
                      className={`max-w-[88%] rounded-xl px-2.5 py-1.5 text-[11px] leading-relaxed ${
                        message.role === 'user'
                          ? 'rounded-tr-sm bg-clinical-primary text-white'
                          : 'rounded-tl-sm border border-surface-border bg-white text-text-secondary'
                      }`}
                    >
                      {message.text}
                    </div>
                  </div>
                ))}
                <div ref={endRef} />
              </div>

              {/* Progreso y pasos */}
              <div>
                <div className="mb-2 flex items-center justify-between">
                  <h3 className="flex items-center gap-1.5 text-[12px] font-bold text-text-primary">
                    <Icon name="fact_check" className="text-[16px] text-sky-600" />
                    {visibleGroup.title}
                  </h3>
                  <span className="font-code-telemetry text-[10px] text-text-muted">
                    Paso {formStep + 1} / {fieldGroups.length}
                  </span>
                </div>
                <div className="h-1.5 overflow-hidden rounded-full bg-surface-subtle">
                  <div
                    className="h-full rounded-full bg-gradient-to-r from-clinical-primary to-sky-500 transition-all duration-300"
                    style={{ width: `${Math.max(progress, 4)}%` }}
                  />
                </div>

                <div className="mt-2.5 flex gap-1.5 overflow-x-auto pb-1">
                  {fieldGroups.map((group, index) => {
                    const isActive = index === formStep
                    const isDone = group.fields.every(field => patientInfo[field.key as keyof PatientInfo]?.trim())
                    const reachable = index <= formStep + 1
                    return (
                      <button
                        key={group.title}
                        type="button"
                        disabled={!reachable}
                        onClick={() => reachable && setFormStep(index)}
                        className={`flex flex-shrink-0 items-center gap-1.5 rounded-lg border px-2 py-1.5 text-[10px] font-semibold transition-all ${
                          isActive
                            ? 'border-sky-300 bg-sky-50 text-clinical-primary shadow-sm'
                            : isDone
                              ? 'border-emerald-200 bg-emerald-50/60 text-emerald-700'
                              : reachable
                                ? 'border-surface-border bg-white text-text-secondary hover:bg-surface-subtle'
                                : 'cursor-not-allowed border-surface-border bg-surface-subtle/50 text-slate-300'
                        }`}
                      >
                        <span className="text-[12px]">{isDone && !isActive ? '✓' : SECTION_ICONS[index]}</span>
                        <span className="max-w-[9.5rem] truncate">{group.title}</span>
                      </button>
                    )
                  })}
                </div>
              </div>

              {/* Campos */}
              <div ref={element => { sectionRefs.current[formStep] = element }}>
                <div className="grid grid-cols-1 gap-2.5 sm:grid-cols-2">
                  {visibleGroup.fields
                    .filter(field => !field.condition || field.condition(patientInfo))
                    .map(field => {
                      const value = patientInfo[field.key as keyof PatientInfo] || ''
                      const filled = Boolean(value.trim())
                      return (
                        <div
                          key={field.key}
                          className={`flex flex-col gap-1 rounded-xl border p-2.5 transition-colors ${
                            filled ? 'border-emerald-100 bg-emerald-50/30' : 'border-surface-border bg-white'
                          } ${field.key === 'triage_discriminators' ? 'sm:col-span-2' : ''}`}
                        >
                          <div className="flex items-center justify-between gap-1">
                            <label className="text-[10px] font-bold uppercase tracking-wider text-text-secondary">
                              {field.label}
                            </label>
                            {filled && <Icon name="check_circle" className="text-[13px] text-emerald-500" filled />}
                          </div>
                          <div className="flex items-stretch gap-1">
                            {field.type === 'select' ? (
                              <select
                                value={value}
                                onChange={event => onFieldChange(field.key, event.target.value)}
                                disabled={isSending}
                                className="patient-field-input w-full rounded-lg border border-transparent bg-surface-subtle px-2 py-1.5 text-[11px] font-medium text-text-primary outline-none transition-all focus:border-sky-200 focus:bg-white focus:ring-2 focus:ring-sky-100 disabled:opacity-60"
                              >
                                <option value="">— Seleccionar —</option>
                                {field.options?.map(option => (
                                  <option key={option.value} value={option.value}>
                                    {option.label}
                                  </option>
                                ))}
                              </select>
                            ) : (
                              <input
                                type="text"
                                placeholder={field.placeholder}
                                value={value}
                                onChange={event => onFieldChange(field.key, event.target.value)}
                                onKeyDown={event => {
                                  if (event.key === 'Enter') goNextField(event.currentTarget)
                                }}
                                disabled={isSending}
                                className="patient-field-input w-full rounded-lg border border-transparent bg-surface-subtle px-2 py-1.5 text-[11px] font-medium text-text-primary outline-none transition-all placeholder:text-slate-400 focus:border-sky-200 focus:bg-white focus:ring-2 focus:ring-sky-100 disabled:opacity-60"
                              />
                            )}
                            {field.suffix && (
                              <span className="flex flex-shrink-0 items-center rounded-lg border border-surface-border bg-white px-1.5 font-code-telemetry text-[9px] text-text-muted">
                                {field.suffix}
                              </span>
                            )}
                          </div>
                        </div>
                      )
                    })}
                </div>
              </div>

              {/* Navegación */}
              <div className="flex flex-wrap items-center justify-between gap-2">
                <button
                  type="button"
                  disabled={formStep === 0}
                  onClick={() => setFormStep(step => Math.max(step - 1, 0))}
                  className="flex items-center gap-1 rounded-xl border border-surface-border bg-white px-3 py-2 text-[11px] font-semibold text-text-secondary transition-colors hover:bg-surface-subtle disabled:cursor-not-allowed disabled:opacity-40"
                >
                  <Icon name="arrow_back" className="text-[16px]" /> Anterior
                </button>

                {!isLastStep ? (
                  <button
                    type="button"
                    onClick={() => setFormStep(step => Math.min(step + 1, fieldGroups.length - 1))}
                    className="flex items-center gap-1 rounded-xl bg-clinical-primary px-3.5 py-2 text-[11px] font-bold text-white shadow-sm transition-all hover:bg-[#072a4a] active:scale-[0.99]"
                  >
                    Siguiente <Icon name="arrow_forward" className="text-[16px]" />
                  </button>
                ) : (
                  <button
                    type="button"
                    onClick={onSubmit}
                    disabled={isSending}
                    className="flex items-center gap-1.5 rounded-xl bg-gradient-to-r from-clinical-primary to-sky-700 px-4 py-2.5 text-[11.5px] font-bold text-white shadow-md transition-all hover:brightness-110 active:scale-[0.99] disabled:opacity-60"
                  >
                    <Icon name={isSending ? 'hourglass_top' : 'play_arrow'} className="text-[18px]" />
                    {isSending ? 'Guardando sesión…' : 'Finalizar y comenzar consulta'}
                  </button>
                )}
              </div>

              {/* Resumen */}
              {isLastStep && (
                <div className="rounded-xl border border-sky-200 bg-sky-50/50 p-3">
                  <h4 className="flex items-center gap-1.5 text-[11px] font-bold text-clinical-primary">
                    <Icon name="assignment" className="text-[16px]" />
                    Resumen antes de iniciar
                  </h4>
                  <div className="mt-2 grid grid-cols-1 gap-2 sm:grid-cols-2">
                    {fieldGroups.map(group => {
                      const filled = group.fields.filter(field => patientInfo[field.key as keyof PatientInfo]?.trim())
                      if (filled.length === 0) return null
                      return (
                        <div key={group.title} className="rounded-lg border border-white bg-white/80 p-2">
                          <strong className="text-[9.5px] font-bold uppercase tracking-wider text-text-muted">
                            {group.title}
                          </strong>
                          <div className="mt-1 flex flex-col gap-0.5">
                            {filled.map(field => (
                              <span key={field.key} className="text-[10px] leading-snug text-text-secondary">
                                <em className="font-semibold not-italic text-text-primary">{field.label}:</em>{' '}
                                {displayValue(field, patientInfo[field.key as keyof PatientInfo] ?? '')}
                              </span>
                            ))}
                          </div>
                        </div>
                      )
                    })}
                  </div>
                </div>
              )}

              {patientInfoMode === 'session_only' && (
                <p className="flex items-start gap-1.5 rounded-lg border border-dashed border-sky-200 bg-sky-50/60 px-2.5 py-1.5 text-[10px] leading-snug text-sky-800">
                  <Icon name="info" className="mt-0.5 text-[14px]" />
                  La identificación del paciente ya existe. Los datos que registres aquí se guardan como
                  una nueva sesión clínica.
                </p>
              )}
            </div>
          </AiWorkspace>
        </div>
      </div>
    </ClinicalShell>
  )
}
