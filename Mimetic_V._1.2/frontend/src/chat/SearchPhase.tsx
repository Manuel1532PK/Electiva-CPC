import { type RefObject } from 'react'
import type { SearchResult } from '../chat/types'
import ClinicalShell from './ClinicalShell'
import { Icon } from './ui'

type Props = {
  user: { name?: string } | null
  onLogout: () => void
  onHistory: () => void
  onResume: () => void
  searchRef: RefObject<HTMLInputElement>
  searchQuery: string
  searching: boolean
  showSearchResults: boolean
  searchResults: SearchResult[]
  onSearchChange: (value: string) => void
  onFocusResults: () => void
  onBlurResults: () => void
  onSelect: (result: SearchResult) => void
  onNewPatient: () => void
}

const DEMO_PATIENTS = [
  { document: '1020304050', name: 'Carlos Mendoza', detail: '3 sesiones · dengue, influenza, gastroenteritis' },
  { document: '1098765432', name: 'María Fernanda López', detail: '2 sesiones · migraña, infección urinaria' },
  { document: '1000000001', name: 'Andrés Ramírez', detail: '2 sesiones · IAM, hipertensión' },
]

function sourceBadge(result: SearchResult) {
  if (result.has_clinical_history && result.has_user_account) {
    return { label: 'Historia + cuenta', className: 'border-emerald-200 bg-emerald-50 text-emerald-700', icon: 'verified' }
  }
  if (result.has_clinical_history) {
    return { label: 'Historia clínica', className: 'border-sky-200 bg-sky-50 text-sky-700', icon: 'clinical_notes' }
  }
  return { label: 'Cuenta de paciente', className: 'border-violet-200 bg-violet-50 text-violet-700', icon: 'person' }
}

export default function SearchPhase({
  user,
  onLogout,
  onHistory,
  onResume,
  searchRef,
  searchQuery,
  searching,
  showSearchResults,
  searchResults,
  onSearchChange,
  onFocusResults,
  onBlurResults,
  onSelect,
  onNewPatient,
}: Props) {
  const hasQuery = searchQuery.trim().length > 0

  return (
    <ClinicalShell
      user={user}
      onLogout={onLogout}
      phase="search"
      onHome={() => {}}
      onNewPatient={onNewPatient}
      onHistory={onHistory}
      onResume={onResume}
      breadcrumb={['Urgencias Hospital Central', 'Búsqueda de paciente']}
    >
      <div className="grid grid-cols-1 items-start gap-4 xl:grid-cols-12">
        {/* ── Buscador ─────────────────────────────────────────── */}
        <section className="flex flex-col gap-4 xl:col-span-8">
          <div className="relative overflow-hidden rounded-2xl border border-surface-border bg-white p-4 shadow-sm sm:p-6">
            <div className="absolute left-0 right-0 top-0 h-1.5 bg-gradient-to-r from-clinical-primary via-sky-600 to-sky-400" />
            <div className="flex flex-wrap items-start justify-between gap-3 pt-1">
              <div>
                <span className="inline-flex items-center gap-1.5 rounded-full border border-sky-200 bg-sky-50 px-2.5 py-1 text-[10px] font-bold uppercase tracking-wider text-sky-800">
                  <Icon name="person_search" className="text-[14px]" />
                  Admisión clínica
                </span>
                <h1 className="mt-2 font-headline-lg text-headline-lg text-clinical-primary">
                  Buscar paciente
                </h1>
                <p className="mt-1 max-w-xl font-body-md text-body-md text-text-secondary">
                  Ingresa el número de documento para abrir la historia clínica existente o iniciar
                  una nueva consulta con identificación completa.
                </p>
              </div>
              <span className="rounded-xl border border-surface-border bg-surface-subtle px-2.5 py-1.5 text-right">
                <span className="block font-code-telemetry text-[9px] uppercase tracking-wider text-text-muted">
                  Sesión clínica
                </span>
                <span className="font-code-telemetry text-[11px] font-bold text-clinical-primary">
                  Guardia A · demo
                </span>
              </span>
            </div>

            <div className="relative mt-5">
              <div className="relative flex items-center">
                <Icon
                  name="search"
                  className="pointer-events-none absolute left-4 text-[22px] text-slate-400"
                />
                <input
                  ref={searchRef}
                  type="text"
                  inputMode="numeric"
                  autoComplete="off"
                  value={searchQuery}
                  onChange={event => onSearchChange(event.target.value)}
                  onFocus={onFocusResults}
                  onBlur={onBlurResults}
                  placeholder="Ingrese el documento del paciente · ej. 1020304050"
                  className="w-full rounded-xl border border-transparent bg-surface-subtle py-3.5 pl-12 pr-32 font-body-lg text-body-lg text-text-primary shadow-inner outline-none transition-all placeholder:text-slate-400 focus:border-sky-200 focus:bg-white focus:ring-4 focus:ring-sky-100"
                  aria-label="Buscar paciente por número de documento"
                />
                <div className="absolute right-2 flex items-center gap-1.5">
                  {searching && (
                    <span className="flex items-center gap-1 rounded-lg bg-white px-2 py-1 text-[10px] font-semibold text-sky-700 shadow-sm">
                      <span className="h-3 w-3 animate-spin rounded-full border-2 border-sky-200 border-t-sky-600" />
                      Buscando
                    </span>
                  )}
                  <span className="hidden rounded-lg bg-white px-2 py-1 font-code-telemetry text-[9.5px] text-text-muted shadow-sm sm:block">
                    Enter
                  </span>
                </div>
              </div>

              {/* Resultados */}
              {showSearchResults && (hasQuery || searchResults.length > 0) && (
                <div className="mimetic-fade-up absolute left-0 right-0 top-full z-30 mt-2 max-h-[24rem] overflow-y-auto rounded-xl border border-surface-border bg-white p-1.5 shadow-2xl shadow-slate-900/10">
                  {searchResults.length > 0 ? (
                    <>
                      <div className="flex items-center justify-between px-2 py-1.5">
                        <span className="text-[9.5px] font-bold uppercase tracking-wider text-text-muted">
                          {searchResults.length} coincidencia(s)
                        </span>
                        <span className="text-[9px] text-text-muted">Selecciona para abrir</span>
                      </div>
                      {searchResults.map(result => {
                        const badge = sourceBadge(result)
                        return (
                          <button
                            key={result.document_number}
                            type="button"
                            onMouseDown={event => {
                              event.preventDefault()
                              onSelect(result)
                            }}
                            onKeyDown={event => {
                              if (event.key === 'Enter' || event.key === ' ') {
                                event.preventDefault()
                                onSelect(result)
                              }
                            }}
                            className="flex w-full items-center gap-3 rounded-lg px-2.5 py-2 text-left transition-colors hover:bg-sky-50"
                          >
                            <div className="flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-xl border border-sky-100 bg-sky-50 text-[11px] font-bold text-clinical-primary">
                              {(result.first_name?.[0] ?? '') + (result.last_name?.[0] ?? '')}
                            </div>
                            <div className="min-w-0 flex-1">
                              <div className="flex flex-wrap items-center gap-1.5">
                                <span className="truncate text-[12px] font-bold text-text-primary">
                                  {result.first_name} {result.last_name}
                                </span>
                                <span className={`rounded border px-1.5 py-0.5 text-[8.5px] font-bold ${badge.className}`}>
                                  {badge.label}
                                </span>
                              </div>
                              <div className="mt-0.5 flex items-center gap-1.5 font-code-telemetry text-[10px] text-text-secondary">
                                <Icon name="badge" className="text-[13px] text-slate-400" />
                                {result.document_type} {result.document_number}
                                {result.base_data?.age && <span>· {result.base_data.age} años</span>}
                                {result.base_data?.city && <span>· {result.base_data.city}</span>}
                              </div>
                            </div>
                            <Icon name="chevron_right" className="text-[20px] text-slate-300" />
                          </button>
                        )
                      })}
                    </>
                  ) : !searching ? (
                    <div className="flex flex-col items-center gap-1 px-4 py-6 text-center">
                      <Icon name="person_off" className="text-[28px] text-slate-300" />
                      <p className="text-[12px] font-semibold text-text-primary">
                        No se encontraron pacientes con ese documento
                      </p>
                      <p className="text-[10.5px] text-text-muted">
                        Puedes registrar una identificación nueva sin historia previa.
                      </p>
                    </div>
                  ) : null}
                </div>
              )}
            </div>

            <div className="mt-4 flex flex-wrap items-center gap-2">
              <button
                type="button"
                onClick={onNewPatient}
                className="flex items-center gap-1.5 rounded-xl bg-clinical-primary px-3.5 py-2.5 text-[11.5px] font-bold text-white shadow-sm transition-all hover:bg-[#072a4a] active:scale-[0.99]"
              >
                <Icon name="person_add" className="text-[17px]" />
                Registrar nuevo paciente
              </button>
              <span className="flex items-center gap-1 text-[10.5px] text-text-muted">
                <Icon name="lock" className="text-[14px]" />
                Acceso restringido a personal asistencial
              </span>
            </div>
          </div>

          <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
            {DEMO_PATIENTS.map(patient => (
              <button
                key={patient.document}
                type="button"
                onClick={() => onSearchChange(patient.document)}
                className="group flex flex-col gap-1 rounded-xl border border-surface-border bg-white p-3 text-left shadow-sm transition-all hover:-translate-y-0.5 hover:border-sky-200 hover:shadow-md"
              >
                <div className="flex items-center justify-between">
                  <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-sky-50 text-sky-700">
                    <Icon name="clinical_notes" className="text-[17px]" />
                  </span>
                  <span className="rounded border border-slate-200 bg-slate-50 px-1.5 py-0.5 font-code-telemetry text-[8.5px] font-bold text-slate-500">
                    demo
                  </span>
                </div>
                <span className="mt-1 text-[12px] font-bold text-text-primary group-hover:text-clinical-primary">
                  {patient.name}
                </span>
                <span className="font-code-telemetry text-[9.5px] text-text-muted">{patient.document}</span>
                <span className="text-[10px] leading-snug text-text-secondary">{patient.detail}</span>
              </button>
            ))}
          </div>
        </section>

        {/* ── Lateral ──────────────────────────────────────────── */}
        <aside className="flex flex-col gap-4 xl:col-span-4">
          <div className="rounded-2xl border border-surface-border bg-white p-4 shadow-sm">
            <div className="flex items-center gap-2">
              <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-clinical-primary text-white">
                <Icon name="smart_toy" className="text-[20px] text-sky-400" />
              </div>
              <div>
                <h2 className="font-headline-sm text-[13px] font-bold text-text-primary">
                  Motor de diagnóstico
                </h2>
                <p className="text-[10px] text-text-muted">Estado de la sesión demo</p>
              </div>
            </div>

            <div className="mt-3 space-y-2">
              {[
                { label: 'Base de conocimiento', value: '276 síntomas · 51 enfermedades', icon: 'database', tone: 'emerald' },
                { label: 'Ontología clínica', value: 'SNOMED-CT / CIE-11', icon: 'account_tree', tone: 'sky' },
                { label: 'Inferencia', value: 'Motor bayesiano local', icon: 'psychology', tone: 'violet' },
              ].map(item => (
                <div
                  key={item.label}
                  className="flex items-center justify-between gap-2 rounded-lg border border-surface-border bg-surface-subtle/60 px-2.5 py-2"
                >
                  <span className="flex items-center gap-1.5 text-[10.5px] text-text-secondary">
                    <Icon
                      name={item.icon}
                      className={`text-[15px] ${
                        item.tone === 'emerald'
                          ? 'text-emerald-600'
                          : item.tone === 'sky'
                            ? 'text-sky-600'
                            : 'text-violet-600'
                      }`}
                    />
                    {item.label}
                  </span>
                  <span className="text-right text-[10px] font-bold text-text-primary">{item.value}</span>
                </div>
              ))}
            </div>

            <div className="mt-3 flex items-center gap-1.5 rounded-lg border border-emerald-200 bg-emerald-50 px-2.5 py-1.5 text-[10px] font-semibold text-emerald-700">
              <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-emerald-500" />
              Backend local conectado · /health
            </div>
          </div>

          <div className="rounded-2xl border border-surface-border bg-white p-4 shadow-sm">
            <h2 className="flex items-center gap-1.5 font-headline-sm text-[13px] font-bold text-text-primary">
              <Icon name="format_list_numbered" className="text-[18px] text-sky-600" />
              Flujo de la consulta
            </h2>
            <ol className="mt-2 space-y-2">
              {[
                { step: '1', title: 'Buscar o registrar', detail: 'Documento, identidad y anamnesis.' },
                { step: '2', title: 'Signos y triaje', detail: 'Vitales, Manchester/ESI y laboratorio.' },
                { step: '3', title: 'Diagnóstico asistido', detail: 'Chat, diferenciales y tratamiento.' },
                { step: '4', title: 'Historia clínica', detail: 'Revisión médica y reporte firmado.' },
              ].map(item => (
                <li key={item.step} className="flex items-start gap-2">
                  <span className="mt-0.5 flex h-5 w-5 flex-shrink-0 items-center justify-center rounded-full bg-sky-100 font-code-telemetry text-[9px] font-bold text-sky-700">
                    {item.step}
                  </span>
                  <span>
                    <span className="block text-[11px] font-bold text-text-primary">{item.title}</span>
                    <span className="block text-[10px] leading-snug text-text-muted">{item.detail}</span>
                  </span>
                </li>
              ))}
            </ol>
          </div>

          <div className="rounded-2xl border border-dashed border-slate-300 bg-white p-3.5">
            <div className="flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-wider text-text-muted">
              <Icon name="science" className="text-[14px] text-violet-500" />
              Alcance de esta demo
            </div>
            <p className="mt-1 text-[10px] leading-relaxed text-text-secondary">
              El diagnóstico y la historia clínica son reales. ECG, FHIR, camas, dictado y MFA son
              visualizaciones simuladas y están marcadas como tales.
            </p>
          </div>
        </aside>
      </div>
    </ClinicalShell>
  )
}
