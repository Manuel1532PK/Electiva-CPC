import { useState, type FormEvent } from 'react'
import { useGoogleLogin } from '@react-oauth/google'
import { apiFetch } from '../api/client'

type SocialProfile = {
  provider: string
  token: string
  email: string
  name: string
}

export default function SocialLogin() {
  const [error, setError] = useState('')
  const [profile, setProfile] = useState<SocialProfile | null>(null)
  const [form, setForm] = useState({
    first_name: '',
    last_name: '',
    document_type: 'CC',
    document_number: '',
    email: '',
    phone: '',
    country: 'Colombia',
    department: '',
    city: '',
    birth_date: '',
    name: '',
  })
  const [submitting, setSubmitting] = useState(false)
  const [verifyEmail, setVerifyEmail] = useState('')
  const [verifyCode, setVerifyCode] = useState('')
  const [verifying, setVerifying] = useState(false)

  const set = (key: string) => (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) =>
    setForm(prev => ({ ...prev, [key]: e.target.value }))

  const handleSocialResponse = async (provider: string, token: string) => {
    setError('')
    try {
      const res = await apiFetch('/api/auth/social-login', {
        method: 'POST',
        auth: false,
        body: JSON.stringify({ provider, token }),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || 'Error al iniciar sesión')

      if (data.new_user) {
        const parts = (data.name || '').trim().split(/\s+/)
        let fn: string, ln: string
        if (parts.length <= 2) {
          fn = parts[0] || ''
          ln = parts.slice(1).join(' ')
        } else if (parts.length === 3) {
          fn = parts[0]
          ln = parts.slice(1).join(' ')
        } else {
          fn = parts.slice(0, 2).join(' ')
          ln = parts.slice(2).join(' ')
        }
        setProfile({ provider, token, email: data.email, name: data.name })
        setForm(prev => ({ ...prev, email: data.email, name: data.name, first_name: fn, last_name: ln }))
      } else {
        localStorage.setItem('token', data.access_token)
        window.location.href = '/'
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al iniciar sesión')
    }
  }

  const confirmRegistration = async () => {
    if (!profile) return
    setError('')
    setSubmitting(true)
    try {
      const body = {
        provider: profile.provider,
        token: profile.token,
        email: form.email,
        name: `${form.first_name} ${form.last_name}`,
        first_name: form.first_name,
        last_name: form.last_name,
        document_type: form.document_type,
        document_number: form.document_number,
        birth_date: form.birth_date,
        country: form.country,
        department: form.department,
        city: form.city,
        phone: form.phone,
      }
      const res = await apiFetch('/api/auth/social-register', {
        method: 'POST',
        auth: false,
        body: JSON.stringify(body),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || 'Error al registrar')
      localStorage.removeItem('token')
      setForm(prev => ({ ...prev, email: data.email || prev.email }))
      setProfile(null)
      setVerifyEmail(data.email || form.email)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al registrar')
    }
    setSubmitting(false)
  }

  const cancelRegistration = () => {
    setProfile(null)
    setForm({
      first_name: '',
      last_name: '',
      document_type: 'CC',
      document_number: '',
      email: '',
      phone: '',
      country: 'Colombia',
      department: '',
      city: '',
      birth_date: '',
      name: '',
    })
    setError('')
  }

  const handleSocialVerify = async (e: FormEvent) => {
    e.preventDefault()
    setError('')
    setVerifying(true)
    try {
      const res = await apiFetch('/api/auth/verify-email', {
        method: 'POST',
        auth: false,
        body: JSON.stringify({ email: verifyEmail, code: verifyCode }),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || 'Error al verificar')
      localStorage.setItem('token', data.access_token)
      window.location.href = '/'
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al verificar')
    }
    setVerifying(false)
  }

  const googleLogin = useGoogleLogin({
    onSuccess: (response) => handleSocialResponse('google', response.access_token),
    onError: () => setError('Inicio de sesión con Google cancelado'),
  })

  if (verifyEmail) {
    return (
      <form className="social-confirm" onSubmit={handleSocialVerify}>
        {error && <div className="auth-error">{error}</div>}
        <div className="social-confirm-header">
          <div className="social-confirm-icon">🔵</div>
          <p>Verifica tu correo para completar el registro</p>
        </div>
        <div className="auth-field">
          <label>Código de verificación</label>
          <input
            type="text"
            placeholder="Ingresa el código de 6 dígitos"
            value={verifyCode}
            onChange={e => setVerifyCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
            required
            maxLength={6}
          />
        </div>
        <p className="auth-hint">
          Enviamos un código de 6 dígitos a <strong>{verifyEmail}</strong>. Es válido por 10 minutos.
        </p>
        {verifyCode.length !== 6 && (
          <p className="auth-hint">Revisa también la carpeta de spam o promociones.</p>
        )}
        <button type="submit" className="auth-btn" disabled={verifying || verifyCode.length !== 6}>
          {verifying ? 'Verificando...' : 'Verificar'}
        </button>
      </form>
    )
  }

  if (profile) {
    return (
      <div className="social-confirm">
        {error && <div className="auth-error">{error}</div>}
        <div className="social-confirm-header">
          <div className="social-confirm-icon">🔵</div>
          <p>Confirma tus datos para completar el registro</p>
        </div>

        <div className="auth-row">
          <div className="auth-field">
            <label>Nombres</label>
            <input type="text" placeholder="Ej: Juan Andrés" value={form.first_name} onChange={set('first_name')} required />
          </div>
          <div className="auth-field">
            <label>Apellidos</label>
            <input type="text" placeholder="Ej: Pérez García" value={form.last_name} onChange={set('last_name')} required />
          </div>
        </div>

        <div className="auth-row">
          <div className="auth-field">
            <label>Tipo de documento</label>
            <select value={form.document_type} onChange={set('document_type')} required>
              <option value="CC">Cédula de Ciudadanía</option>
              <option value="CE">Cédula de Extranjería</option>
              <option value="TI">Tarjeta de Identidad</option>
              <option value="Pasaporte">Pasaporte</option>
              <option value="Otro">Otro</option>
            </select>
          </div>
          <div className="auth-field">
            <label>Número de documento</label>
            <input type="text" placeholder="Ej: 1234567890" value={form.document_number} onChange={set('document_number')} required />
          </div>
        </div>

        <div className="auth-field">
          <label>Fecha de nacimiento</label>
          <input type="date" value={form.birth_date} onChange={set('birth_date')} required />
        </div>

        <div className="auth-field">
          <label>Correo electrónico</label>
          <input type="email" value={form.email} onChange={set('email')} required />
        </div>

        <div className="auth-field">
          <label>Teléfono de contacto</label>
          <input type="tel" placeholder="Ej: 3001234567" value={form.phone} onChange={set('phone')} required />
        </div>

        <div className="auth-row auth-row-3">
          <div className="auth-field">
            <label>País</label>
            <input type="text" placeholder="Ej: Colombia" value={form.country} onChange={set('country')} required />
          </div>
          <div className="auth-field">
            <label>Departamento</label>
            <input type="text" placeholder="Ej: Cundinamarca" value={form.department} onChange={set('department')} required />
          </div>
          <div className="auth-field">
            <label>Ciudad</label>
            <input type="text" placeholder="Ej: Bogotá" value={form.city} onChange={set('city')} required />
          </div>
        </div>

        <button className="auth-btn" onClick={confirmRegistration} disabled={submitting}>
          {submitting ? 'Registrando...' : 'Confirmar y continuar'}
        </button>
        <button className="auth-btn cancel" onClick={cancelRegistration}>
          Cancelar
        </button>
      </div>
    )
  }

  return (
    <>
      {error && <div className="auth-error">{error}</div>}
      <div className="social-login">
        <button className="social-btn google" onClick={() => googleLogin()}>
          <svg viewBox="0 0 24 24" width="18" height="18"><path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z"/><path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/><path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/><path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/></svg>
          Continuar con Google
        </button>
      </div>
    </>
  )
}
