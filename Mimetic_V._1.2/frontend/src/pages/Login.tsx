import { useEffect, useState, type FormEvent } from 'react'
import { Link, Navigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import SocialLogin from '../components/SocialLogin'
import '../styles/mimetic.css'

type MfaMode = 'totp' | 'hardware' | 'sms'

type HealthState = {
  database: 'connected' | 'degraded' | 'offline'
  latency: number | null
}

const MFA_MODES: { id: MfaMode; label: string; icon: string; placeholder: string }[] = [
  { id: 'totp', label: 'App TOTP', icon: 'phonelink_lock', placeholder: '000000' },
  { id: 'hardware', label: 'Hardware FIPS', icon: 'key', placeholder: 'YUBI-XXXX' },
  { id: 'sms', label: 'SMS Seguro', icon: 'sms', placeholder: '000000' },
]

const inputClass =
  'field-ring w-full rounded-lg border border-transparent bg-surface-container-low py-3 pl-11 pr-4 font-body-md text-body-md text-on-surface transition-all placeholder:text-outline focus:bg-surface-container-lowest'

export default function Login() {
  const { user, login } = useAuth()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [mfaMode, setMfaMode] = useState<MfaMode>('totp')
  const [mfaCode, setMfaCode] = useState('')
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [health, setHealth] = useState<HealthState>({ database: 'offline', latency: null })
  const [sessionId] = useState(
    () => `MIM-${Math.random().toString(36).slice(2, 8).toUpperCase()}`,
  )

  useEffect(() => {
    let active = true
    const started = performance.now()

    fetch('/health')
      .then(res => res.json())
      .then(data => {
        if (!active) return
        setHealth({
          database: data?.database === 'connected' ? 'connected' : 'degraded',
          latency: Math.round(performance.now() - started),
        })
      })
      .catch(() => {
        if (active) setHealth({ database: 'offline', latency: null })
      })

    return () => {
      active = false
    }
  }, [])

  if (user) return <Navigate to="/" replace />

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError('')
    setNotice('')
    setSubmitting(true)
    try {
      await login(email.trim(), password)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al iniciar sesión')
    }
    setSubmitting(false)
  }

  const showNotice = (message: string) => {
    setError('')
    setNotice(message)
  }

  const activeMfa = MFA_MODES.find(mode => mode.id === mfaMode) ?? MFA_MODES[0]

  const healthLabel =
    health.database === 'connected'
      ? 'Conectada'
      : health.database === 'degraded'
        ? 'Degradada'
        : 'Sin conexión'

  const healthTone =
    health.database === 'connected'
      ? 'text-secondary-fixed'
      : health.database === 'degraded'
        ? 'text-[#ffd28a]'
        : 'text-[#ffb4ab]'

  return (
    <div className="mimetic-auth flex min-h-screen flex-col bg-background font-body text-on-surface">
      <main className="relative w-full flex-1 overflow-hidden px-4 py-10 md:px-6 md:py-14">
        <div className="pointer-events-none absolute -left-20 -top-32 h-96 w-96 rounded-full bg-secondary-fixed/30 blur-3xl" />
        <div className="pointer-events-none absolute -right-32 top-1/2 h-80 w-80 rounded-full bg-secondary-container/20 blur-3xl" />

        <div className="relative mx-auto w-full max-w-5xl">
          <div className="mb-8 flex flex-col items-center text-center">
            <div className="mb-4 flex items-center gap-2 rounded-full bg-surface-container-high px-4 py-1 text-secondary shadow-sm">
              <span className="h-2 w-2 animate-pulse rounded-full bg-secondary" />
              <span className="font-telemetry-sm text-telemetry-sm font-semibold uppercase tracking-wider">
                Plataforma clínica · Acceso seguro
              </span>
            </div>

            <div className="mb-2 flex items-center justify-center gap-3">
              <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary-container text-on-primary shadow-md">
                <span className="material-symbols-outlined text-[28px]" aria-hidden="true">
                  biotech
                </span>
              </div>
              <div className="flex flex-col text-left">
                <span className="font-headline-md text-headline-md tracking-tight text-primary">
                  MIMETIC
                </span>
                <span className="-mt-1 font-telemetry-sm text-telemetry-sm font-medium uppercase tracking-wider text-secondary">
                  BioDigital Intelligence
                </span>
              </div>
            </div>

            <h1 className="mb-1 max-w-2xl font-headline-lg text-headline-lg tracking-tight text-primary">
              Iniciar sesión en MIMETIC
            </h1>
            <p className="max-w-xl font-body-md text-body-md text-on-surface-variant">
              Ingreso unificado a la historia clínica, el asistente de diagnóstico y la
              trazabilidad de cada atención.
            </p>
          </div>

          <div className="grid grid-cols-1 items-start gap-6 lg:grid-cols-12">
            {/* ── Formulario ─────────────────────────────────────── */}
            <div className="rounded-xl bg-surface-container-lowest p-5 shadow-xl md:p-8 lg:col-span-8">
              <form className="flex flex-col gap-5" onSubmit={handleSubmit}>
                {error && (
                  <div
                    role="alert"
                    className="flex items-start gap-2 rounded-lg border border-[#ffb4ab] bg-error-container px-3.5 py-3 font-body-sm text-body-sm text-on-error-container"
                  >
                    <span className="material-symbols-outlined text-[18px]" aria-hidden="true">
                      error
                    </span>
                    <span>{error}</span>
                  </div>
                )}

                {notice && (
                  <div
                    role="status"
                    className="flex items-start gap-2 rounded-lg border border-[#bae6fd] bg-[#f0f9ff] px-3.5 py-3 font-body-sm text-body-sm text-[#075985]"
                  >
                    <span className="material-symbols-outlined text-[18px]" aria-hidden="true">
                      info
                    </span>
                    <span>{notice}</span>
                  </div>
                )}

                <div className="flex flex-col gap-1">
                  <label
                    className="flex items-center justify-between font-title-sm text-title-sm text-primary"
                    htmlFor="userEmail"
                  >
                    <span>Usuario institucional / Correo sanitario</span>
                    <span className="font-telemetry-sm text-telemetry-sm font-normal text-on-surface-variant">
                      Identificador único
                    </span>
                  </label>
                  <div className="relative flex items-center">
                    <span
                      className="material-symbols-outlined pointer-events-none absolute left-4 text-[20px] text-on-surface-variant"
                      aria-hidden="true"
                    >
                      badge
                    </span>
                    <input
                      id="userEmail"
                      type="email"
                      autoComplete="email"
                      className={inputClass}
                      placeholder="usuario@mimetic.health o correo corporativo"
                      value={email}
                      onChange={e => setEmail(e.target.value)}
                      required
                    />
                  </div>
                  <p className="flex items-center gap-1 font-body-sm text-body-sm text-on-surface-variant">
                    <span className="material-symbols-outlined text-[14px] text-secondary" aria-hidden="true">
                      verified
                    </span>
                    Usa el correo con el que tu hospital registró tu cuenta.
                  </p>
                </div>

                <div className="flex flex-col gap-1">
                  <div className="flex items-center justify-between">
                    <label className="font-title-sm text-title-sm text-primary" htmlFor="passwordField">
                      Contraseña de acceso
                    </label>
                    <button
                      type="button"
                      className="font-telemetry-sm text-telemetry-sm font-medium text-secondary transition-colors hover:text-primary"
                      onClick={() =>
                        showNotice(
                          'La recuperación automática de contraseña no está habilitada. Contacta al administrador de tu hospital o a la mesa de ayuda.',
                        )
                      }
                    >
                      ¿Olvidó su contraseña?
                    </button>
                  </div>
                  <div className="relative flex items-center">
                    <span
                      className="material-symbols-outlined pointer-events-none absolute left-4 text-[20px] text-on-surface-variant"
                      aria-hidden="true"
                    >
                      lock
                    </span>
                    <input
                      id="passwordField"
                      type={showPassword ? 'text' : 'password'}
                      autoComplete="current-password"
                      className={`${inputClass} pr-11`}
                      placeholder="••••••••••••••••"
                      value={password}
                      onChange={e => setPassword(e.target.value)}
                      required
                    />
                    <button
                      type="button"
                      className="absolute right-4 text-on-surface-variant transition-colors hover:text-primary focus:outline-none"
                      aria-label={showPassword ? 'Ocultar contraseña' : 'Mostrar contraseña'}
                      onClick={() => setShowPassword(value => !value)}
                    >
                      <span className="material-symbols-outlined text-[20px]" aria-hidden="true">
                        {showPassword ? 'visibility_off' : 'visibility'}
                      </span>
                    </button>
                  </div>
                </div>

                {/* MFA: presente en el prototipo, aún no validado por el backend */}
                <div className="flex flex-col gap-2 pt-1">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <span className="font-title-sm text-title-sm text-primary">
                      Segundo factor de autenticación (MFA)
                    </span>
                    <span className="rounded-full border border-[#bae6fd] bg-[#f0f9ff] px-2 py-0.5 font-telemetry-sm text-telemetry-sm font-semibold text-[#075985]">
                      Demo · no requerido
                    </span>
                  </div>

                  <div className="grid grid-cols-3 gap-1 rounded-lg bg-surface-container-low p-1">
                    {MFA_MODES.map(mode => {
                      const base =
                        'flex items-center justify-center gap-1.5 rounded px-1 py-2 font-title-sm text-title-sm transition-all'
                      const active = 'bg-surface-container-lowest text-primary shadow-sm'
                      const inactive = 'text-on-surface-variant hover:text-primary'
                      return (
                        <button
                          key={mode.id}
                          type="button"
                          className={`${base} ${mfaMode === mode.id ? active : inactive}`}
                          aria-pressed={mfaMode === mode.id}
                          onClick={() => {
                            setMfaMode(mode.id)
                            setMfaCode('')
                          }}
                        >
                          <span
                            className={`material-symbols-outlined text-[18px] ${
                              mfaMode === mode.id ? 'text-secondary' : ''
                            }`}
                            aria-hidden="true"
                          >
                            {mode.icon}
                          </span>
                          <span className="truncate">{mode.label}</span>
                        </button>
                      )
                    })}
                  </div>

                  <div className="flex flex-col items-center justify-between gap-3 rounded-lg bg-surface-container-low p-3 md:flex-row">
                    <div className="flex w-full items-center gap-2 md:w-auto">
                      <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-secondary-fixed text-primary">
                        <span className="material-symbols-outlined text-[22px]" aria-hidden="true">
                          pin
                        </span>
                      </div>
                      <div className="flex flex-col">
                        <span className="font-title-sm text-title-sm text-primary">
                          Código dinámico
                        </span>
                        <span className="font-body-sm text-body-sm text-on-surface-variant">
                          Simulación visual, no se envía al servidor
                        </span>
                      </div>
                    </div>
                    <div className="flex w-full items-center justify-end gap-2 md:w-auto">
                      <input
                        type="text"
                        inputMode={mfaMode === 'hardware' ? 'text' : 'numeric'}
                        maxLength={mfaMode === 'hardware' ? 9 : 6}
                        className="field-ring w-36 rounded-lg bg-surface-container-lowest px-3 py-2 text-center font-telemetry-lg text-telemetry-lg tracking-widest text-primary focus:outline-none"
                        placeholder={activeMfa.placeholder}
                        value={mfaCode}
                        onChange={e => setMfaCode(e.target.value.toUpperCase().slice(0, mfaMode === 'hardware' ? 9 : 6))}
                        aria-label="Código de segundo factor"
                      />
                      <div className="flex h-9 items-center gap-1 rounded bg-surface-container-high px-2 font-telemetry-sm text-telemetry-sm text-on-surface-variant">
                        <span className="material-symbols-outlined text-[18px]" aria-hidden="true">
                          science
                        </span>
                        <span className="font-semibold">Demo</span>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="flex items-start gap-2 pt-1">
                  <input
                    id="hospitalSession"
                    type="checkbox"
                    defaultChecked
                    className="mt-1 h-4 w-4 cursor-pointer rounded text-primary focus:ring-0 focus:outline-none"
                  />
                  <label
                    className="cursor-pointer select-none font-body-md text-body-md text-on-surface"
                    htmlFor="hospitalSession"
                  >
                    <span className="font-semibold text-primary">
                      Mantener sesión iniciada en este equipo
                    </span>
                    <span className="block font-body-sm text-body-sm text-on-surface-variant">
                      El token de acceso expira a las 24 horas.
                    </span>
                  </label>
                </div>

                <div className="flex flex-col items-center gap-3 pt-1 sm:flex-row">
                  <button
                    type="submit"
                    disabled={submitting}
                    className="group flex w-full items-center justify-center gap-2 rounded-lg bg-primary px-6 py-3.5 font-title-md text-title-md font-bold text-on-primary shadow-md transition-all hover:bg-primary-container hover:shadow-lg disabled:cursor-not-allowed disabled:opacity-80 sm:flex-1"
                  >
                    <span
                      className={`material-symbols-outlined text-[20px] ${submitting ? 'animate-spin' : 'transition-transform group-hover:translate-x-0.5'}`}
                      aria-hidden="true"
                    >
                      {submitting ? 'progress_activity' : 'lock_open'}
                    </span>
                    <span>{submitting ? 'Autenticando…' : 'Ingresar al sistema clínico'}</span>
                    {!submitting && (
                      <span
                        className="material-symbols-outlined text-[20px] transition-transform group-hover:translate-x-1"
                        aria-hidden="true"
                      >
                        arrow_forward
                      </span>
                    )}
                  </button>

                  <button
                    type="button"
                    className="flex w-full items-center justify-center gap-2 rounded-lg bg-surface-container-high px-4 py-3.5 font-title-sm text-title-sm font-semibold text-primary transition-colors hover:bg-surface-container-highest sm:w-auto"
                    onClick={() =>
                      showNotice(
                        'WebAuthn / YubiKey está contemplado en el prototipo, pero todavía no está habilitado en el backend.',
                      )
                    }
                  >
                    <span className="material-symbols-outlined text-[20px] text-secondary" aria-hidden="true">
                      key
                    </span>
                    <span className="whitespace-nowrap">WebAuthn / YubiKey</span>
                  </button>
                </div>
              </form>

              <div className="mt-5 flex flex-wrap items-center justify-between gap-2 border-t border-surface-container-high pt-4">
                <button
                  type="button"
                  className="flex items-center gap-1 font-body-sm text-body-sm font-medium text-secondary transition-colors hover:text-primary"
                  onClick={() =>
                    showNotice(
                      'Solicita el desbloqueo o la creación de credenciales al administrador de tu hospital.',
                    )
                  }
                >
                  <span className="material-symbols-outlined text-[16px]" aria-hidden="true">
                    lock_reset
                  </span>
                  Solicitar desbloqueo de credenciales
                </button>
                <span className="font-telemetry-sm text-telemetry-sm text-on-surface-variant">
                  Sesión ID: <span className="font-semibold text-primary">{sessionId}</span>
                </span>
              </div>

              <div className="mt-5">
                <div className="social-divider">
                  <span>O continúa con</span>
                </div>
                <SocialLogin />
                <p className="auth-footer">
                  ¿No tienes cuenta? <Link to="/register">Regístrate</Link>
                </p>
              </div>
            </div>

            {/* ── Panel lateral ───────────────────────────────────── */}
            <aside className="flex flex-col gap-4 lg:col-span-4">
              <div className="relative overflow-hidden rounded-xl bg-primary p-5 text-on-primary shadow-lg">
                <div className="pointer-events-none absolute -bottom-8 -right-8 h-36 w-36 rounded-full bg-secondary-container/10" />

                <div className="mb-4 flex items-center gap-2">
                  <span className="material-symbols-outlined text-[24px] text-secondary-fixed" aria-hidden="true">
                    security
                  </span>
                  <span className="font-title-sm text-title-sm font-bold tracking-tight">
                    Estándares y seguridad médica
                  </span>
                </div>

                <div className="flex flex-col gap-4">
                  <div className="flex items-start gap-2">
                    <span className="material-symbols-outlined mt-0.5 text-[20px] text-secondary-fixed" aria-hidden="true">
                      enhanced_encryption
                    </span>
                    <div className="flex flex-col">
                      <span className="font-title-sm text-title-sm font-semibold text-surface-container-lowest">
                        Credenciales protegidas
                      </span>
                      <span className="font-body-sm text-body-sm text-primary-fixed-dim">
                        Contraseñas con hash bcrypt y tokens JWT firmados con expiración de 24 horas.
                      </span>
                    </div>
                  </div>

                  <div className="flex items-start gap-2">
                    <span className="material-symbols-outlined mt-0.5 text-[20px] text-secondary-fixed" aria-hidden="true">
                      verified_user
                    </span>
                    <div className="flex flex-col">
                      <span className="font-title-sm text-title-sm font-semibold text-surface-container-lowest">
                        Acceso por rol y hospital
                      </span>
                      <span className="font-body-sm text-body-sm text-primary-fixed-dim">
                        Cada usuario queda asociado a su rol clínico y a su hospital de origen.
                      </span>
                    </div>
                  </div>

                  <div className="flex items-start gap-2">
                    <span className="material-symbols-outlined mt-0.5 text-[20px] text-secondary-fixed" aria-hidden="true">
                      history_edu
                    </span>
                    <div className="flex flex-col">
                      <span className="font-title-sm text-title-sm font-semibold text-surface-container-lowest">
                        Trazabilidad de la atención
                      </span>
                      <span className="font-body-sm text-body-sm text-primary-fixed-dim">
                        Cada consulta y diagnóstico queda vinculado al profesional que lo registró.
                      </span>
                    </div>
                  </div>
                </div>

                <div className="-mx-5 -mb-5 mt-5 flex items-center justify-between rounded-b-xl bg-primary-container/40 p-4">
                  <div className="flex flex-col">
                    <span className="font-telemetry-sm text-telemetry-sm text-primary-fixed-dim">
                      BASE DE DATOS
                    </span>
                    <span className={`font-telemetry-lg text-telemetry-lg font-bold ${healthTone}`}>
                      {healthLabel}
                    </span>
                  </div>
                  <div className="flex flex-col text-right">
                    <span className="font-telemetry-sm text-telemetry-sm text-primary-fixed-dim">
                      LATENCIA API
                    </span>
                    <span className="font-telemetry-sm text-telemetry-sm font-bold text-secondary-fixed">
                      {health.latency === null ? '—' : `${health.latency} ms`}
                    </span>
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-3 rounded-xl bg-surface-container-low p-4">
                <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-surface-container-highest text-secondary">
                  <span className="material-symbols-outlined text-[22px]" aria-hidden="true">
                    contact_support
                  </span>
                </div>
                <div className="flex min-w-0 flex-col">
                  <span className="font-title-sm text-title-sm font-bold text-primary">
                    Mesa de ayuda TI
                  </span>
                  <span className="truncate font-body-sm text-body-sm text-on-surface-variant">
                    Contacta al administrador de tu hospital
                  </span>
                  <span className="font-telemetry-sm text-telemetry-sm font-medium text-secondary">
                    Soporte de acceso, credenciales y roles
                  </span>
                </div>
              </div>
            </aside>
          </div>
        </div>
      </main>

      <footer className="w-full border-t border-surface-container-high bg-surface-container-lowest py-5">
        <div className="mx-auto flex w-full max-w-5xl flex-col items-center justify-between gap-3 px-4 text-center md:flex-row md:text-left">
          <div className="flex flex-col items-center gap-1 md:flex-row md:gap-4">
            <span className="font-telemetry-sm text-telemetry-sm text-on-surface-variant">
              © 2026 MIMETIC BioDigital Intelligence
            </span>
            <span className="hidden text-outline-variant md:inline">•</span>
            <span className="font-telemetry-sm text-telemetry-sm text-on-surface-variant">
              Entorno de desarrollo · Datos de demostración
            </span>
          </div>
          <div className="flex items-center gap-4">
            <button
              type="button"
              className="font-telemetry-sm text-telemetry-sm text-on-surface-variant transition-colors hover:text-primary"
              onClick={() => showNotice('La política de privacidad se publicará antes del despliegue productivo.')}
            >
              Privacidad
            </button>
            <button
              type="button"
              className="font-telemetry-sm text-telemetry-sm text-on-surface-variant transition-colors hover:text-primary"
              onClick={() => showNotice('Los términos de servicio se publicarán antes del despliegue productivo.')}
            >
              Términos
            </button>
            <button
              type="button"
              className="font-telemetry-sm text-telemetry-sm font-medium text-secondary transition-colors hover:text-primary"
              onClick={() => showNotice('Escríbenos a soporte@mimetic.health para asistencia.')}
            >
              Mesa de ayuda 24/7
            </button>
          </div>
        </div>
      </footer>
    </div>
  )
}
