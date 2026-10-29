import { useState, type ReactNode } from 'react'
import type { Phase } from './types'
import { Icon, initials, Modal, ROLE_LABEL, useToast } from './ui'

type Props = {
  user: { name?: string; role?: string } | null
  onLogout: () => void
  phase: Phase
  onHome: () => void
  onNewPatient: () => void
  onHistory: () => void
  onResume: () => void
  breadcrumb: string[]
  children: ReactNode
}

const NAV_ITEMS = [
  { id: 'search', label: 'Búsqueda de paciente', icon: 'person_search' },
  { id: 'new', label: 'Nueva consulta', icon: 'person_add' },
  { id: 'symptoms', label: 'Panel clínico', icon: 'monitor_heart' },
  { id: 'history', label: 'Historial clínico', icon: 'folder_shared' },
  { id: 'fhir', label: 'Interoperabilidad FHIR', icon: 'hub' },
  { id: 'settings', label: 'Configuración', icon: 'settings' },
] as const

export default function ClinicalShell({
  user,
  onLogout,
  phase,
  onHome,
  onNewPatient,
  onHistory,
  onResume,
  breadcrumb,
  children,
}: Props) {
  const showToast = useToast()
  const [pendingExit, setPendingExit] = useState<'home' | 'new' | 'history' | null>(null)

  const activeNav =
    phase === 'search'
      ? 'search'
      : phase === 'patient_info'
        ? 'new'
        : phase === 'history'
          ? 'history'
          : 'symptoms'

  const requestNavigation = (target: 'home' | 'new' | 'history') => {
    if (phase === 'history') {
      if (target === 'home') return onHome()
      if (target === 'new') return onNewPatient()
      return
    }
    if (phase === 'search') {
      if (target === 'new') return onNewPatient()
      if (target === 'home') return onHome()
      if (target === 'history') return onHistory()
      return
    }
    return setPendingExit(target)
  }

  const confirmExit = () => {
    if (pendingExit === 'home') onHome()
    if (pendingExit === 'new') onNewPatient()
    if (pendingExit === 'history') onHistory()
    setPendingExit(null)
  }

  const handleNav = (id: (typeof NAV_ITEMS)[number]['id']) => {
    if (id === 'search') return requestNavigation('home')
    if (id === 'new') return requestNavigation('new')
    if (id === 'symptoms') {
      if (phase === 'symptoms') return
      if (phase === 'patient_info' || phase === 'report') return onResume()
      return showToast('Abre una atención desde el historial o inicia una nueva consulta.', {
        icon: 'info',
        tone: 'info',
      })
    }
    if (id === 'history') {
      if (phase === 'history') return
      return requestNavigation('history')
    }
    if (id === 'fhir') {
      return showToast('FHIR R4 vive en Historial clínico → pestaña FHIR (mapeo simulado).', {
        icon: 'hub',
        tone: 'info',
      })
    }
    return showToast('Configuración clínica disponible en el panel de administración.', {
      icon: 'settings',
      tone: 'info',
    })
  }

  const roleLabel = ROLE_LABEL[user?.role ?? 'medico'] ?? 'Médico asistencial'
  const userInitials = initials(user?.name)

  return (
    <div className="mimetic-ui min-h-screen bg-surface-canvas text-text-primary">
      {/* ── Sidebar ─────────────────────────────────────────────── */}
      <aside className="fixed left-0 top-0 z-50 hidden h-screen w-64 flex-col justify-between overflow-y-auto border-r border-surface-border bg-white shadow-[2px_0_12px_rgba(15,23,42,0.03)] xl:flex">
        <div className="flex flex-col">
          <div className="flex h-20 flex-shrink-0 items-center gap-3 border-b border-surface-border/80 bg-white px-4">
            <div className="flex w-full items-center justify-between">
              <img
                src="/logo.png"
                alt="MIMETIC — Réplica Virtual, Decisiones Reales"
                className="h-9 w-auto object-contain"
              />
              <div className="flex flex-col items-end">
                <span className="font-headline-sm text-[10.5px] font-extrabold uppercase tracking-widest text-clinical-primary">
                  CORE AI
                </span>
                <span className="font-code-telemetry text-[9px] font-semibold text-text-muted">
                  v4.2 PRO
                </span>
              </div>
            </div>
          </div>

          <div className="flex flex-col gap-1 px-3 py-4">
            <span className="px-2 pb-1 text-[10px] font-bold uppercase tracking-[0.12em] text-text-muted">
              Espacio de trabajo
            </span>
            {NAV_ITEMS.map(item => {
              const active = item.id === activeNav
              return (
                <button
                  key={item.id}
                  type="button"
                  onClick={() => handleNav(item.id)}
                  className={`group flex items-center gap-2.5 rounded-lg px-2.5 py-2 text-left text-xs font-semibold transition-colors ${
                    active
                      ? 'bg-sky-50 text-clinical-primary ring-1 ring-inset ring-sky-200'
                      : 'text-text-secondary hover:bg-surface-subtle hover:text-clinical-primary'
                  }`}
                  aria-current={active ? 'page' : undefined}
                >
                  <Icon
                    name={item.icon}
                    className={`text-[19px] ${active ? 'text-clinical-accent' : 'text-slate-400 group-hover:text-sky-600'}`}
                    filled={active}
                  />
                  <span className="truncate">{item.label}</span>
                  {item.id === 'symptoms' && phase === 'symptoms' && (
                    <span className="ml-auto h-1.5 w-1.5 rounded-full bg-emerald-500" />
                  )}
                </button>
              )
            })}
          </div>

          <div className="mx-3 rounded-xl border border-surface-border bg-surface-subtle/70 p-3">
            <div className="flex items-center justify-between">
              <span className="flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-wider text-text-secondary">
                <span className="relative flex h-2 w-2">
                  <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-70" />
                  <span className="relative inline-flex h-2 w-2 rounded-full bg-emerald-500" />
                </span>
                Motor clínico
              </span>
              <Icon name="bolt" className="text-[15px] text-amber-500" filled />
            </div>
            <p className="mt-1.5 text-[11px] leading-relaxed text-text-secondary">
              Ontología SNOMED-CT / CIE-11 con inferencia bayesiana.
            </p>
            <div className="mt-2 flex flex-wrap gap-1">
              <span className="rounded border border-emerald-200 bg-emerald-50 px-1.5 py-0.5 font-code-telemetry text-[9px] font-semibold text-emerald-700">
                51 enfermedades
              </span>
              <span className="rounded border border-sky-200 bg-sky-50 px-1.5 py-0.5 font-code-telemetry text-[9px] font-semibold text-sky-700">
                276 síntomas
              </span>
            </div>
          </div>

          <div className="mx-3 mt-3 rounded-xl border border-dashed border-slate-300 bg-white p-3">
            <div className="flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-wider text-text-muted">
              <Icon name="science" className="text-[14px] text-violet-500" />
              Roadmap visible
            </div>
            <ul className="mt-1.5 space-y-1 text-[10.5px] text-text-secondary">
              <li>· FHIR R4 y WebAuthn</li>
              <li>· Camas y quirófano</li>
              <li>· Dictado clínico</li>
            </ul>
          </div>
        </div>

        <div className="border-t border-surface-border bg-white p-3">
          <div className="flex items-center gap-2.5">
            <div className="flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-xl bg-gradient-to-tr from-clinical-primary to-sky-600 text-xs font-bold text-white shadow-sm ring-2 ring-sky-100">
              {userInitials}
            </div>
            <div className="min-w-0 flex-1">
              <p className="truncate text-xs font-bold text-text-primary">{user?.name ?? 'Médico'}</p>
              <p className="flex items-center gap-1 truncate text-[10px] text-text-muted">
                <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
                {roleLabel}
              </p>
            </div>
            <button
              type="button"
              onClick={onLogout}
              className="rounded-lg p-1.5 text-slate-400 transition-colors hover:bg-rose-50 hover:text-rose-600"
              title="Cerrar sesión"
              aria-label="Cerrar sesión"
            >
              <Icon name="logout" className="text-[19px]" />
            </button>
          </div>
        </div>
      </aside>

      {/* ── Contenido ───────────────────────────────────────────── */}
      <div className="flex min-h-screen flex-col xl:pl-64">
        <header className="fixed left-0 right-0 top-0 z-40 flex h-16 items-center justify-between border-b border-surface-border bg-white/95 px-3 shadow-sm backdrop-blur-md sm:px-6 xl:left-64">
          <div className="flex min-w-0 items-center gap-2 sm:gap-4">
            <div className="flex items-center gap-2 border-r border-surface-border pr-2 xl:hidden">
              <img src="/logo.png" alt="MIMETIC" className="h-7 w-auto object-contain" />
            </div>

            <div className="flex items-center gap-2 rounded-full border border-sky-200 bg-sky-50 px-2.5 py-1 text-[11px] font-semibold text-sky-900 sm:px-3 sm:text-xs">
              <span className="relative flex h-2 w-2 flex-shrink-0">
                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-sky-400 opacity-70" />
                <span className="relative inline-flex h-2 w-2 rounded-full bg-sky-600" />
              </span>
              <span className="max-w-[120px] truncate sm:max-w-none">Guardia A · UCI Urgencias</span>
            </div>

            <div className="hidden items-center gap-2 rounded-full border border-surface-border bg-surface-subtle px-3 py-1 text-[11px] text-text-secondary lg:flex">
              <Icon name="router" className="text-[16px] text-sky-600" />
              <span className="font-code-telemetry text-[10.5px]">
                IoT Gateway: <strong className="text-clinical-primary">Online</strong>
              </span>
              <span className="rounded bg-white px-1 text-[9px] font-bold uppercase text-text-muted">
                demo
              </span>
            </div>
          </div>

          <div className="flex items-center gap-1.5 sm:gap-2.5">
            <button
              type="button"
              onClick={() =>
                showToast('Modo de contingencia offline simulado. La caché local no está implementada.', {
                  icon: 'cloud_off',
                  tone: 'warn',
                })
              }
              className="hidden items-center gap-2 rounded-xl border border-surface-border bg-surface-subtle px-3 py-1.5 text-[11px] font-semibold text-text-secondary transition-colors hover:bg-white hover:text-text-primary md:flex"
              title="Modo de contingencia (simulado)"
            >
              <Icon name="cloud_sync" className="text-[17px] text-text-muted" />
              Contingencia
            </button>

            <button
              type="button"
              onClick={() =>
                showToast('Centro de alertas clínicas: sin alertas nuevas en esta sesión demo.', {
                  icon: 'notifications',
                  tone: 'info',
                })
              }
              className="relative rounded-xl border border-surface-border p-2 text-text-secondary transition-colors hover:bg-surface-subtle hover:text-text-primary"
              aria-label="Alertas clínicas"
            >
              <Icon name="notifications" className="text-[20px]" />
              <span className="absolute right-1.5 top-1.5 h-2 w-2 animate-pulse rounded-full bg-rose-500 ring-2 ring-white" />
            </button>

            <div className="mx-0.5 hidden h-6 w-px bg-surface-border sm:block" />

            <div className="flex items-center gap-2 rounded-xl p-1 text-left">
              <div className="hidden flex-col text-right sm:flex">
                <span className="text-[12.5px] font-bold leading-tight text-text-primary">
                  {user?.name ?? 'Médico'}
                </span>
                <span className="flex items-center justify-end gap-1 text-[10.5px] font-medium text-sky-600">
                  <span className="h-1.5 w-1.5 rounded-full bg-sky-500" />
                  {roleLabel}
                </span>
              </div>
              <div className="relative">
                <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-tr from-clinical-primary to-sky-600 text-[12px] font-bold text-white shadow-sm ring-2 ring-sky-200">
                  {userInitials}
                </div>
                <span className="absolute -bottom-0.5 -right-0.5 h-2.5 w-2.5 rounded-full bg-sky-500 ring-2 ring-white" />
              </div>
            </div>

            <button
              type="button"
              onClick={onLogout}
              className="rounded-lg p-1.5 text-slate-400 transition-colors hover:bg-rose-50 hover:text-rose-600 xl:hidden"
              aria-label="Cerrar sesión"
            >
              <Icon name="logout" className="text-[19px]" />
            </button>
          </div>
        </header>

        <main className="min-h-screen w-full overflow-x-hidden bg-surface-canvas pt-16">
          <div className="mx-auto flex w-full max-w-[1780px] flex-col gap-4 px-3 pb-24 pt-4 sm:px-6 sm:pt-5 lg:px-8">
            {/* Breadcrumb */}
            <div className="flex flex-wrap items-center justify-between gap-2.5 rounded-xl border border-surface-border bg-white px-3.5 py-2.5 shadow-sm">
              <div className="flex min-w-0 flex-wrap items-center gap-1.5 text-[11px] sm:text-xs">
                <Icon name="clinical_notes" className="text-[18px] text-sky-600" />
                {breadcrumb.map((crumb, index) => {
                  const last = index === breadcrumb.length - 1
                  return (
                    <span key={`${crumb}-${index}`} className="flex items-center gap-1.5">
                      {index > 0 && <span className="text-slate-300">/</span>}
                      <span
                        className={
                          last
                            ? 'rounded-md border border-sky-200 bg-sky-50 px-2 py-0.5 font-bold text-clinical-primary'
                            : 'font-medium text-text-secondary'
                        }
                      >
                        {crumb}
                      </span>
                    </span>
                  )
                })}
              </div>

              <div className="flex flex-wrap items-center gap-1.5">
                <span className="inline-flex items-center gap-1.5 rounded-lg border border-sky-200 bg-sky-50 px-2.5 py-1 text-[10.5px] font-semibold text-sky-800">
                  <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-sky-500" />
                  Telemetría demo
                </span>
                <span className="inline-flex items-center gap-1 rounded-lg border border-slate-200 bg-slate-100 px-2 py-1 font-code-telemetry text-[10px] text-slate-600">
                  RNF15 ≤ 3 clics
                </span>
              </div>
            </div>

            {/* Navegación móvil del shell */}
            <div className="flex items-center gap-1.5 overflow-x-auto rounded-xl border border-surface-border bg-white p-1.5 shadow-sm xl:hidden">
              {[
                { id: 'search' as const, label: 'Buscar', icon: 'person_search', target: 'home' as const },
                { id: 'new' as const, label: 'Nueva consulta', icon: 'person_add', target: 'new' as const },
                { id: 'history' as const, label: 'Historial', icon: 'folder_shared', target: 'history' as const },
              ].map(item => {
                const active = activeNav === item.id
                return (
                  <button
                    key={item.id}
                    type="button"
                    onClick={() => requestNavigation(item.target)}
                    className={`flex flex-shrink-0 items-center gap-1 rounded-lg px-2.5 py-1.5 text-[11px] font-semibold transition-colors ${
                      active
                        ? 'bg-sky-50 font-bold text-clinical-primary ring-1 ring-inset ring-sky-200'
                        : 'text-text-secondary hover:bg-surface-subtle'
                    }`}
                  >
                    <Icon name={item.icon} className="text-[16px]" /> {item.label}
                  </button>
                )
              })}
              <button
                type="button"
                onClick={() => handleNav('symptoms')}
                className={`flex flex-shrink-0 items-center gap-1 rounded-lg px-2.5 py-1.5 text-[11px] font-semibold transition-colors ${
                  activeNav === 'symptoms'
                    ? 'bg-sky-50 font-bold text-clinical-primary ring-1 ring-inset ring-sky-200'
                    : 'text-text-secondary hover:bg-surface-subtle'
                }`}
              >
                <Icon name="monitor_heart" className="text-[16px]" /> Panel clínico
              </button>
            </div>

            {children}
          </div>
        </main>
      </div>

      <Modal
        open={pendingExit !== null}
        onClose={() => setPendingExit(null)}
        icon="warning"
        title={
          pendingExit === 'new'
            ? 'Iniciar otra consulta'
            : pendingExit === 'history'
              ? 'Abrir el historial clínico'
              : 'Volver a la búsqueda'
        }
        subtitle="La sesión actual no se ha guardado por completo"
        footer={
          <>
            <button
              type="button"
              onClick={() => setPendingExit(null)}
              className="rounded-xl bg-surface-subtle px-3.5 py-2 text-[11px] font-semibold text-text-secondary transition-colors hover:text-text-primary"
            >
              Continuar aquí
            </button>
            <button
              type="button"
              onClick={confirmExit}
              className="rounded-xl bg-clinical-primary px-3.5 py-2 text-[11px] font-bold text-white transition-colors hover:bg-[#072a4a]"
            >
              {pendingExit === 'new'
                ? 'Sí, nueva consulta'
                : pendingExit === 'history'
                  ? 'Sí, abrir historial'
                  : 'Sí, ir a búsqueda'}
            </button>
          </>
        }
      >
        <p className="text-[11.5px] leading-relaxed text-text-secondary">
          Si sales ahora se descartan los síntomas, diagnósticos y ajustes que aún no se hayan
          convertido en historia clínica. Los datos ya guardados en el backend no se eliminan y
          seguirán disponibles en el historial del paciente.
        </p>
      </Modal>
    </div>
  )
}
