import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useRef,
  useState,
  type ReactNode,
} from 'react'

/* ── Iconos ─────────────────────────────────────────────────────── */

export function Icon({
  name,
  className = '',
  filled = false,
}: {
  name: string
  className?: string
  filled?: boolean
}) {
  return (
    <span
      className={`material-symbols-outlined ${className}`}
      style={filled ? { fontVariationSettings: "'FILL' 1, 'wght' 400, 'GRAD' 0, 'opsz' 24" } : undefined}
      aria-hidden="true"
    >
      {name}
    </span>
  )
}

/* ── Toasts ─────────────────────────────────────────────────────── */

type ToastTone = 'ok' | 'warn' | 'info' | 'error'

type ToastItem = {
  id: number
  message: string
  icon: string
  tone: ToastTone
}

type ShowToast = (message: string, options?: { icon?: string; tone?: ToastTone }) => void

const ToastContext = createContext<ShowToast>(() => {})

export const useToast = () => useContext(ToastContext)

const TONE_CLASS: Record<ToastTone, string> = {
  ok: 'border-emerald-200 bg-white text-slate-800',
  warn: 'border-amber-200 bg-amber-50 text-amber-900',
  info: 'border-sky-200 bg-sky-50 text-sky-900',
  error: 'border-rose-200 bg-rose-50 text-rose-900',
}

const TONE_ICON: Record<ToastTone, string> = {
  ok: 'text-emerald-600',
  warn: 'text-amber-600',
  info: 'text-sky-600',
  error: 'text-rose-600',
}

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<ToastItem[]>([])
  const timers = useRef<ReturnType<typeof setTimeout>[]>([])

  useEffect(() => {
    return () => {
      timers.current.forEach(clearTimeout)
    }
  }, [])

  const showToast = useCallback<ShowToast>((message, options) => {
    const item: ToastItem = {
      id: Date.now() + Math.random(),
      message,
      icon: options?.icon ?? 'check_circle',
      tone: options?.tone ?? 'ok',
    }
    setToasts(current => [...current.slice(-2), item])
    const timer = setTimeout(() => {
      setToasts(current => current.filter(t => t.id !== item.id))
    }, 4200)
    timers.current.push(timer)
  }, [])

  return (
    <ToastContext.Provider value={showToast}>
      {children}
      <div className="pointer-events-none fixed bottom-6 right-4 z-[70] flex w-[min(24rem,calc(100vw-2rem))] flex-col gap-2 sm:right-6">
        {toasts.map(toast => (
          <div
            key={toast.id}
            role="status"
            className={`mimetic-fade-up pointer-events-auto flex items-start gap-2.5 rounded-xl border px-4 py-3 shadow-xl shadow-slate-900/10 ${TONE_CLASS[toast.tone]}`}
          >
            <Icon name={toast.icon} className={`text-[20px] ${TONE_ICON[toast.tone]}`} />
            <span className="pt-0.5 text-xs font-semibold leading-relaxed">{toast.message}</span>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  )
}

/* ── Modal ──────────────────────────────────────────────────────── */

export function Modal({
  open,
  onClose,
  icon = 'info',
  title,
  subtitle,
  children,
  footer,
}: {
  open: boolean
  onClose: () => void
  icon?: string
  title: string
  subtitle?: string
  children: ReactNode
  footer?: ReactNode
}) {
  useEffect(() => {
    if (!open) return
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', onKeyDown)
    return () => window.removeEventListener('keydown', onKeyDown)
  }, [open, onClose])

  if (!open) return null

  return (
    <div
      className="fixed inset-0 z-[60] flex items-center justify-center bg-slate-900/50 p-4 backdrop-blur-sm"
      role="dialog"
      aria-modal="true"
      aria-label={title}
      onClick={onClose}
    >
      <div
        className="mimetic-fade-up flex w-full max-w-lg flex-col gap-4 rounded-2xl border border-slate-200 bg-white p-5 shadow-2xl"
        onClick={event => event.stopPropagation()}
      >
        <div className="flex items-start justify-between gap-3 border-b border-slate-200 pb-3">
          <div className="flex items-center gap-2.5">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-sky-50 text-sky-700">
              <Icon name={icon} className="text-[20px]" />
            </div>
            <div>
              <h3 className="font-headline-sm text-base font-bold text-slate-900">{title}</h3>
              {subtitle && <p className="text-[11px] text-slate-500">{subtitle}</p>}
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="rounded-lg p-1 text-slate-400 transition-colors hover:bg-slate-100 hover:text-slate-700"
            aria-label="Cerrar"
          >
            <Icon name="close" className="text-[20px]" />
          </button>
        </div>
        <div className="flex flex-col gap-3 text-xs text-slate-600">{children}</div>
        {footer && (
          <div className="flex items-center justify-end gap-2 border-t border-slate-200 pt-3">{footer}</div>
        )}
      </div>
    </div>
  )
}

/* ── Helpers visuales ───────────────────────────────────────────── */

export function initials(name?: string): string {
  if (!name) return 'MD'
  return name
    .replace(/^(Dra?\.?|Dr\.?)\s+/i, '')
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map(part => part[0]?.toUpperCase() ?? '')
    .join('')
}

export function genderLabel(gender?: string): string {
  if (!gender) return 'Sin dato'
  const value = gender.toLowerCase()
  if (value.startsWith('m') && !value.startsWith('muj')) return 'Masculino'
  if (value.startsWith('f') || value.startsWith('muj')) return 'Femenino'
  return gender
}

export const ROLE_LABEL: Record<string, string> = {
  medico: 'Médico asistencial',
  admin: 'Administrador',
  super_admin: 'Superadministrador',
  paciente: 'Paciente',
}
