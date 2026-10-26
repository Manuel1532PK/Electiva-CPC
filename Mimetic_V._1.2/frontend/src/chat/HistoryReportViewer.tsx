import { useCallback, useEffect, useRef } from 'react'
import { Icon, useToast } from './ui'

export type ViewerDocument = {
  html: string
  title: string
  subtitle: string
  patientName: string
  documentNumber: string
  sourceLabel: string
  fileBase: string
  /** Abre el diálogo de impresión al cargar el documento (Guardar como PDF). */
  autoPrint?: boolean
}

type Props = {
  document: ViewerDocument
  onClose: () => void
}

function safeFileBase(value: string) {
  return (
    value
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '')
      .replace(/[^a-zA-Z0-9-_]+/g, '-')
      .replace(/^-+|-+$/g, '')
      .toLowerCase() || 'documento'
  )
}

export default function HistoryReportViewer({ document: viewerDoc, onClose }: Props) {
  const showToast = useToast()
  const frameRef = useRef<HTMLIFrameElement>(null)
  const printedRef = useRef(false)

  const applyDocumentTitle = useCallback(() => {
    const frame = frameRef.current
    const doc = frame?.contentDocument
    if (!doc) return
    try {
      doc.title = `${viewerDoc.fileBase}`
    } catch {
      /* El navegador puede restringir el acceso si el documento no es same-origin. */
    }
  }, [viewerDoc.fileBase])

  const printDocument = useCallback(
    (fromPdfButton: boolean) => {
      const frame = frameRef.current
      if (!frame?.contentWindow) {
        showToast('El navegador no permite imprimir este visor. Abre el documento en otra pestaña.', {
          icon: 'warning',
          tone: 'warn',
        })
        return
      }
      applyDocumentTitle()
      try {
        frame.contentWindow.focus()
        frame.contentWindow.print()
        showToast(
          fromPdfButton
            ? 'En el diálogo de impresión elige «Guardar como PDF» para descargar el expediente.'
            : 'Diálogo de impresión abierto. Puedes imprimir o guardar como PDF.',
          { icon: fromPdfButton ? 'picture_as_pdf' : 'print', tone: 'info' },
        )
      } catch {
        showToast('No se pudo abrir el diálogo de impresión. Usa «Abrir» y luego imprime.', {
          icon: 'warning',
          tone: 'warn',
        })
      }
    },
    [applyDocumentTitle, showToast],
  )

  useEffect(() => {
    const previousOverflow = window.document.body.style.overflow
    window.document.body.style.overflow = 'hidden'
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', onKeyDown)
    return () => {
      window.document.body.style.overflow = previousOverflow
      window.removeEventListener('keydown', onKeyDown)
    }
  }, [onClose])

  const handleLoad = () => {
    applyDocumentTitle()
    if (viewerDoc.autoPrint && !printedRef.current) {
      printedRef.current = true
      window.setTimeout(() => printDocument(true), 300)
    }
  }

  const buildBlob = () => new Blob([viewerDoc.html], { type: 'text/html;charset=utf-8' })

  const handleDownloadHtml = () => {
    const url = URL.createObjectURL(buildBlob())
    const link = window.document.createElement('a')
    link.href = url
    link.download = `${safeFileBase(viewerDoc.fileBase)}.html`
    window.document.body.appendChild(link)
    link.click()
    link.remove()
    URL.revokeObjectURL(url)
    showToast('Documento descargado en HTML. Para PDF usa «Descargar PDF».', {
      icon: 'download',
      tone: 'info',
    })
  }

  const handleOpen = () => {
    const url = URL.createObjectURL(buildBlob())
    const opened = window.open(url, '_blank', 'noopener,noreferrer')
    if (!opened) {
      showToast('El navegador bloqueó la pestaña nueva. Permite ventanas emergentes.', {
        icon: 'warning',
        tone: 'warn',
      })
    }
    window.setTimeout(() => URL.revokeObjectURL(url), 60_000)
  }

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(viewerDoc.html)
      showToast('HTML del documento copiado al portapapeles.', { icon: 'content_copy' })
    } catch {
      showToast('El navegador bloqueó el portapapeles. Usa la descarga del documento.', {
        icon: 'warning',
        tone: 'warn',
      })
    }
  }

  return (
    <div
      className="fixed inset-0 z-[65] flex items-center justify-center bg-slate-900/60 p-1.5 backdrop-blur-sm sm:p-4"
      role="dialog"
      aria-modal="true"
      aria-label={viewerDoc.title}
      onClick={onClose}
    >
      <div
        className="mimetic-fade-up flex h-[96vh] w-full max-w-[1320px] flex-col overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-2xl"
        onClick={event => event.stopPropagation()}
      >
        <header className="flex flex-wrap items-center justify-between gap-2 border-b border-surface-border bg-gradient-to-r from-white via-white to-sky-50/60 px-3 py-2.5">
          <div className="flex min-w-0 items-center gap-2.5">
            <div className="flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-xl bg-clinical-primary text-sky-300">
              <Icon name="description" className="text-[20px]" />
            </div>
            <div className="min-w-0">
              <div className="flex flex-wrap items-center gap-1.5">
                <h2 className="truncate font-headline-sm text-[13px] font-bold text-text-primary">
                  {viewerDoc.title}
                </h2>
                <span className="rounded border border-sky-200 bg-sky-50 px-1.5 py-0.5 text-[8.5px] font-bold uppercase text-sky-800">
                  {viewerDoc.sourceLabel}
                </span>
              </div>
              <p className="truncate text-[10px] text-text-muted">{viewerDoc.subtitle}</p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-1.5">
            <button
              type="button"
              onClick={() => printDocument(false)}
              className="flex items-center gap-1 rounded-lg border border-surface-border bg-white px-2 py-1.5 text-[10px] font-semibold text-text-secondary transition-colors hover:bg-surface-subtle hover:text-text-primary"
              title="Imprimir"
            >
              <Icon name="print" className="text-[15px]" />
              <span className="hidden sm:inline">Imprimir</span>
            </button>
            <button
              type="button"
              onClick={() => printDocument(true)}
              className="flex items-center gap-1 rounded-lg bg-clinical-primary px-2.5 py-1.5 text-[10px] font-bold text-white transition-colors hover:bg-[#072a4a]"
              title="Descargar PDF mediante el diálogo de impresión"
            >
              <Icon name="picture_as_pdf" className="text-[15px]" />
              Descargar PDF
            </button>
            <button
              type="button"
              onClick={handleDownloadHtml}
              className="flex items-center gap-1 rounded-lg border border-surface-border bg-white px-2 py-1.5 text-[10px] font-semibold text-text-secondary transition-colors hover:bg-surface-subtle hover:text-text-primary"
              title="Descargar HTML"
            >
              <Icon name="download" className="text-[15px]" />
              <span className="hidden md:inline">HTML</span>
            </button>
            <button
              type="button"
              onClick={handleOpen}
              className="flex items-center gap-1 rounded-lg border border-surface-border bg-white px-2 py-1.5 text-[10px] font-semibold text-text-secondary transition-colors hover:bg-surface-subtle hover:text-text-primary"
              title="Abrir en pestaña nueva"
            >
              <Icon name="open_in_new" className="text-[15px]" />
              <span className="hidden md:inline">Abrir</span>
            </button>
            <button
              type="button"
              onClick={() => void handleCopy()}
              className="flex items-center gap-1 rounded-lg border border-sky-200 bg-sky-50 px-2 py-1.5 text-[10px] font-bold text-sky-800 transition-colors hover:bg-sky-100"
              title="Copiar HTML"
            >
              <Icon name="content_copy" className="text-[15px]" />
              <span className="hidden md:inline">Copiar</span>
            </button>
            <button
              type="button"
              onClick={onClose}
              className="ml-0.5 rounded-lg p-1.5 text-slate-400 transition-colors hover:bg-rose-50 hover:text-rose-600"
              aria-label="Cerrar vista previa"
            >
              <Icon name="close" className="text-[20px]" />
            </button>
          </div>
        </header>

        <div className="flex min-h-0 flex-1 flex-col lg:flex-row">
          <aside className="hidden w-60 flex-shrink-0 flex-col gap-3 overflow-y-auto border-r border-surface-border bg-surface-subtle/40 p-3.5 lg:flex">
            <div>
              <span className="text-[9px] font-bold uppercase tracking-wider text-text-muted">
                Paciente
              </span>
              <p className="mt-0.5 text-[12.5px] font-bold text-text-primary">{viewerDoc.patientName}</p>
              <p className="font-code-telemetry text-[10.5px] text-text-secondary">
                {viewerDoc.documentNumber || 'Sin documento'}
              </p>
            </div>

            <div className="rounded-xl border border-surface-border bg-white p-2.5">
              <span className="flex items-center gap-1 text-[9.5px] font-bold uppercase tracking-wider text-text-muted">
                <Icon name="info" className="text-[13px] text-sky-600" />
                Cómo obtener el PDF
              </span>
              <p className="mt-1 text-[10.5px] leading-relaxed text-text-secondary">
                Pulsa <strong className="text-text-primary">Descargar PDF</strong> y elige
                <strong className="text-text-primary"> Guardar como PDF</strong> en el diálogo del
                navegador. El archivo no se envía a ningún servidor.
              </p>
            </div>

            <div className="rounded-xl border border-dashed border-slate-300 bg-white p-2.5">
              <span className="flex items-center gap-1 text-[9.5px] font-bold uppercase tracking-wider text-text-muted">
                <Icon name="verified_user" className="text-[13px] text-emerald-600" />
                Alcance
              </span>
              <p className="mt-1 text-[10px] leading-relaxed text-text-secondary">
                Documento de demostración. La firma electrónica y el envío al HIS institucional
                están en roadmap.
              </p>
            </div>

            <div className="mt-auto rounded-lg border border-surface-border bg-white px-2.5 py-2 font-code-telemetry text-[9.5px] text-text-muted">
              MIMETIC v4.2 · {new Date().toLocaleDateString('es-CO')}
            </div>
          </aside>

          <div className="relative min-h-0 flex-1 bg-surface-subtle p-1.5 sm:p-2.5">
            <iframe
              ref={frameRef}
              srcDoc={viewerDoc.html}
              onLoad={handleLoad}
              title={viewerDoc.title}
              className="h-full min-h-[60vh] w-full rounded-xl border border-surface-border bg-white shadow-inner"
            />
          </div>
        </div>
      </div>
    </div>
  )
}
