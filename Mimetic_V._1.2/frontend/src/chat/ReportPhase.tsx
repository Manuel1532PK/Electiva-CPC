import { useMemo, useRef } from 'react'
import type { DoctorReview, PatientInfo } from './types'
import ClinicalShell from './ClinicalShell'
import { Icon, useToast } from './ui'

type Props = {
  user: { name?: string } | null
  onLogout: () => void
  patientInfo: PatientInfo
  doctorReview: DoctorReview
  reportHtml: string
  onBack: () => void
  onReset: () => void
  onNewPatient: () => void
  onHistory: () => void
  onResume: () => void
}

export default function ReportPhase({
  user,
  onLogout,
  patientInfo,
  doctorReview,
  reportHtml,
  onBack,
  onReset,
  onNewPatient,
  onHistory,
  onResume,
}: Props) {
  const showToast = useToast()
  const frameRef = useRef<HTMLIFrameElement>(null)

  const patientLabel =
    patientInfo.name || `${patientInfo.first_name ?? ''} ${patientInfo.last_name ?? ''}`.trim() || 'Paciente'

  const confirmed = useMemo(
    () => [...doctorReview.confirmedDiagnoses, ...doctorReview.manualDiagnoses.map(item => item.disease_name)],
    [doctorReview.confirmedDiagnoses, doctorReview.manualDiagnoses],
  )

  const buildBlob = () =>
    new Blob([reportHtml], { type: 'text/html;charset=utf-8' })

  const handlePrint = () => {
    const frame = frameRef.current
    if (!frame?.contentWindow) {
      showToast('El navegador no permite imprimir el visor. Abre el documento en una pestaña.', {
        icon: 'warning',
        tone: 'warn',
      })
      return
    }
    frame.contentWindow.focus()
    frame.contentWindow.print()
  }

  const handleDownload = () => {
    const url = URL.createObjectURL(buildBlob())
    const link = document.createElement('a')
    const doc = (patientInfo.id_document || 'paciente').replace(/\s+/g, '-')
    link.href = url
    link.download = `historia-clinica-${doc}.html`
    document.body.appendChild(link)
    link.click()
    link.remove()
    URL.revokeObjectURL(url)
    showToast('Historia clínica descargada como HTML.', { icon: 'download' })
  }

  const handleOpenTab = () => {
    const url = URL.createObjectURL(buildBlob())
    const opened = window.open(url, '_blank', 'noopener,noreferrer')
    if (!opened) {
      showToast('El navegador bloqueó la nueva pestaña. Permite ventanas emergentes e inténtalo de nuevo.', {
        icon: 'warning',
        tone: 'warn',
      })
    }
    setTimeout(() => URL.revokeObjectURL(url), 60_000)
  }

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(reportHtml)
      showToast('HTML de la historia clínica copiado al portapapeles.', { icon: 'content_copy' })
    } catch {
      showToast('El navegador bloqueó el portapapeles. Usa la descarga del documento.', {
        icon: 'warning',
        tone: 'warn',
      })
    }
  }

  return (
    <ClinicalShell
      user={user}
      onLogout={onLogout}
      phase="report"
      onHome={onReset}
      onNewPatient={onNewPatient}
      onHistory={onHistory}
      onResume={onResume}
      breadcrumb={['Urgencias Hospital Central', patientLabel, 'Historia clínica']}
    >
      <div className="grid grid-cols-1 items-start gap-4 xl:grid-cols-12">
        {/* ── Resumen de la historia ────────────────────────────── */}
        <aside className="flex flex-col gap-4 xl:col-span-4">
          <section className="overflow-hidden rounded-2xl border border-surface-border bg-white shadow-sm">
            <div className="h-1.5 bg-gradient-to-r from-emerald-500 via-emerald-400 to-sky-400" />
            <div className="p-3.5">
              <span className="inline-flex items-center gap-1.5 rounded-full border border-emerald-200 bg-emerald-50 px-2.5 py-1 text-[10px] font-bold uppercase tracking-wider text-emerald-700">
                <Icon name="task_alt" className="text-[14px]" filled />
                Historia generada
              </span>
              <h1 className="mt-2 font-headline-sm text-[17px] font-bold leading-tight text-text-primary">
                {patientLabel}
              </h1>
              <p className="mt-0.5 font-code-telemetry text-[10.5px] text-text-secondary">
                {patientInfo.document_type || 'CC'} {patientInfo.id_document || 'sin documento'}
                {patientInfo.age ? ` · ${patientInfo.age} años` : ''}
              </p>
              <p className="mt-2 flex items-start gap-1.5 rounded-lg border border-surface-border bg-surface-subtle px-2.5 py-1.5 text-[10px] leading-snug text-text-secondary">
                <Icon name="info" className="mt-0.5 text-[14px] text-sky-600" />
                El documento se generó con los diagnósticos confirmados, los medicamentos seleccionados y las
                notas del médico.
              </p>
            </div>
            <div className="grid grid-cols-2 gap-2 border-t border-surface-border p-3">
              <div className="rounded-xl border border-surface-border bg-surface-subtle p-2.5">
                <span className="block text-[9px] font-bold uppercase tracking-wider text-text-muted">
                  Diagnósticos
                </span>
                <span className="font-headline-sm text-lg font-black text-clinical-primary">
                  {confirmed.length}
                </span>
              </div>
              <div className="rounded-xl border border-surface-border bg-surface-subtle p-2.5">
                <span className="block text-[9px] font-bold uppercase tracking-wider text-text-muted">
                  Medicamentos
                </span>
                <span className="font-headline-sm text-lg font-black text-clinical-primary">
                  {doctorReview.selectedMedicines.length}
                </span>
              </div>
            </div>
          </section>

          <section className="rounded-2xl border border-surface-border bg-white p-3.5 shadow-sm">
            <h2 className="flex items-center gap-1.5 font-headline-sm text-[12.5px] font-bold text-text-primary">
              <Icon name="fact_check" className="text-[17px] text-emerald-600" />
              Cierre clínico
            </h2>

            <div className="mt-2">
              <span className="text-[9.5px] font-bold uppercase tracking-wider text-text-muted">
                Diagnósticos confirmados
              </span>
              {confirmed.length > 0 ? (
                <div className="mt-1 flex flex-wrap gap-1">
                  {confirmed.map(diagnosis => (
                    <span
                      key={diagnosis}
                      className="rounded-full border border-emerald-200 bg-emerald-50 px-2 py-0.5 text-[9.5px] font-semibold text-emerald-700"
                    >
                      {diagnosis}
                    </span>
                  ))}
                </div>
              ) : (
                <p className="mt-1 text-[10.5px] italic text-text-muted">Sin diagnósticos confirmados.</p>
              )}
            </div>

            <div className="mt-3">
              <span className="text-[9.5px] font-bold uppercase tracking-wider text-text-muted">
                Medicamentos incluidos
              </span>
              {doctorReview.selectedMedicines.length > 0 ? (
                <ul className="mt-1 flex flex-col gap-0.5">
                  {doctorReview.selectedMedicines.map(medicine => (
                    <li key={medicine} className="flex items-start gap-1 text-[10.5px] text-text-secondary">
                      <Icon name="medication" className="mt-0.5 text-[13px] text-sky-600" />
                      <span className="min-w-0">
                        {medicine}
                        {doctorReview.modifiedDoses[medicine] && (
                          <em className="ml-1 text-[9.5px] text-amber-700">
                            (ajuste: {doctorReview.modifiedDoses[medicine]})
                          </em>
                        )}
                      </span>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="mt-1 text-[10.5px] italic text-text-muted">Sin medicamentos seleccionados.</p>
              )}
            </div>

            {doctorReview.doctorNotes.trim() && (
              <div className="mt-3 rounded-xl border border-sky-100 bg-sky-50/60 p-2.5">
                <span className="text-[9.5px] font-bold uppercase tracking-wider text-sky-800">
                  Notas del médico
                </span>
                <p className="mt-1 whitespace-pre-wrap text-[10.5px] leading-relaxed text-sky-950">
                  {doctorReview.doctorNotes}
                </p>
              </div>
            )}
          </section>

          <div className="grid grid-cols-2 gap-2">
            <button
              type="button"
              onClick={onBack}
              className="flex items-center justify-center gap-1.5 rounded-xl border border-surface-border bg-white px-2.5 py-2.5 text-[11px] font-semibold text-text-secondary shadow-sm transition-colors hover:bg-surface-subtle hover:text-text-primary"
            >
              <Icon name="arrow_back" className="text-[16px]" />
              Volver al diagnóstico
            </button>
            <button
              type="button"
              onClick={onNewPatient}
              className="flex items-center justify-center gap-1.5 rounded-xl bg-clinical-primary px-2.5 py-2.5 text-[11px] font-bold text-white shadow-sm transition-all hover:bg-[#072a4a] active:scale-[0.99]"
            >
              <Icon name="person_add" className="text-[16px]" />
              Nueva consulta
            </button>
          </div>

          <p className="px-1 text-[9.5px] leading-snug text-text-muted">
            Documento de demostración. La firma electrónica y el envío a la historia institucional están en
            roadmap; el HTML se genera localmente y no sale de este equipo.
          </p>
        </aside>

        {/* ── Visor del documento ──────────────────────────────── */}
        <section className="flex min-w-0 flex-col overflow-hidden rounded-2xl border border-surface-border bg-white shadow-sm xl:col-span-8">
          <header className="flex flex-wrap items-center justify-between gap-2 border-b border-surface-border bg-gradient-to-r from-white via-white to-sky-50/50 p-3">
            <div className="flex min-w-0 items-center gap-2.5">
              <div className="flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-xl bg-clinical-primary text-white">
                <Icon name="description" className="text-[20px] text-sky-400" />
              </div>
              <div className="min-w-0">
                <h2 className="truncate font-headline-sm text-[13px] font-bold text-text-primary">
                  Historia clínica · vista previa
                </h2>
                <p className="text-[10px] text-text-muted">
                  Documento HTML generado por Mimetic Medical Engine
                </p>
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-1.5">
              <button
                type="button"
                onClick={handlePrint}
                className="flex items-center gap-1 rounded-lg border border-surface-border bg-white px-2 py-1.5 text-[10px] font-semibold text-text-secondary transition-colors hover:bg-surface-subtle hover:text-text-primary"
                title="Imprimir"
              >
                <Icon name="print" className="text-[15px]" />
                <span className="hidden sm:inline">Imprimir</span>
              </button>
              <button
                type="button"
                onClick={handleDownload}
                className="flex items-center gap-1 rounded-lg border border-surface-border bg-white px-2 py-1.5 text-[10px] font-semibold text-text-secondary transition-colors hover:bg-surface-subtle hover:text-text-primary"
                title="Descargar HTML"
              >
                <Icon name="download" className="text-[15px]" />
                <span className="hidden sm:inline">Descargar</span>
              </button>
              <button
                type="button"
                onClick={handleOpenTab}
                className="flex items-center gap-1 rounded-lg border border-surface-border bg-white px-2 py-1.5 text-[10px] font-semibold text-text-secondary transition-colors hover:bg-surface-subtle hover:text-text-primary"
                title="Abrir en pestaña nueva"
              >
                <Icon name="open_in_new" className="text-[15px]" />
                <span className="hidden sm:inline">Abrir</span>
              </button>
              <button
                type="button"
                onClick={handleCopy}
                className="flex items-center gap-1 rounded-lg border border-sky-200 bg-sky-50 px-2 py-1.5 text-[10px] font-bold text-sky-800 transition-colors hover:bg-sky-100"
                title="Copiar HTML"
              >
                <Icon name="content_copy" className="text-[15px]" />
                <span className="hidden sm:inline">Copiar</span>
              </button>
            </div>
          </header>

          <div className="relative flex-1 bg-surface-subtle p-2 sm:p-3">
            <iframe
              ref={frameRef}
              srcDoc={reportHtml}
              title="Reporte Clínico"
              className="h-[70vh] w-full rounded-xl border border-surface-border bg-white shadow-inner xl:h-[calc(100vh-13.5rem)]"
            />
          </div>

          <footer className="flex flex-wrap items-center justify-between gap-1.5 border-t border-surface-border bg-white px-3 py-2 font-code-telemetry text-[9.5px] text-text-muted">
            <span className="flex items-center gap-1">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
              Documento listo · {new Date().toLocaleDateString('es-CO')}
            </span>
            <span>MIMETIC v4.2 · demo local</span>
          </footer>
        </section>
      </div>
    </ClinicalShell>
  )
}
