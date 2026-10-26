import { useState, type FormEvent, useMemo, useEffect } from 'react'
import { Link, Navigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { apiFetch } from '../api/client'
import { getAllCountries, getDepartments, getCities, type LocationOption } from '../data/locations'

export default function Register() {
  const { user } = useAuth()
  const [form, setForm] = useState({
    first_name: '',
    last_name: '',
    document_type: 'CC',
    document_number: '',
    email: '',
    phone: '',
    country: '',
    department: '',
    city: '',
    birth_date: '',
    name: '',
    password: '',
  })
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [step, setStep] = useState<'form' | 'verify'>('form')
  const [code, setCode] = useState('')
  const [verifying, setVerifying] = useState(false)
  const [cities, setCities] = useState<LocationOption[]>([])
  const [loadingCities, setLoadingCities] = useState(false)

  const countries: LocationOption[] = useMemo(() => getAllCountries(), [])
  const departments: LocationOption[] = useMemo(
    () => (form.country ? getDepartments(form.country) : []),
    [form.country],
  )

  useEffect(() => {
    if (!form.country || !form.department) {
      setCities([])
      return
    }
    let cancelled = false
    setLoadingCities(true)
    getCities(form.country, form.department)
      .then(result => {
        if (!cancelled) setCities(result)
      })
      .catch(() => {
        if (!cancelled) setCities([])
      })
      .finally(() => {
        if (!cancelled) setLoadingCities(false)
      })
    return () => {
      cancelled = true
    }
  }, [form.country, form.department])

  const set = (key: string) => (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) =>
    setForm(prev => ({ ...prev, [key]: e.target.value }))

  const handleCountryChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const country = e.target.value
    setForm(prev => ({ ...prev, country, department: '', city: '' }))
  }

  const handleDepartmentChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const department = e.target.value
    setForm(prev => ({ ...prev, department, city: '' }))
  }

  const cityName = cities.find(c => c.code === form.city)?.name ?? form.city

  const countryName = countries.find(c => c.code === form.country)?.name ?? form.country
  const departmentName = departments.find(d => d.code === form.department)?.name ?? form.department

  if (user) return <Navigate to="/" replace />

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError('')
    setSubmitting(true)
    try {
      const body = {
        ...form,
        country: countryName,
        department: departmentName,
        city: cityName,
        name: `${form.first_name} ${form.last_name}`,
      }
      const res = await apiFetch('/api/auth/register', {
        method: 'POST',
        auth: false,
        body: JSON.stringify(body),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || 'Registration failed')
      setStep('verify')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al registrar')
    }
    setSubmitting(false)
  }

  const handleVerify = async (e: FormEvent) => {
    e.preventDefault()
    setError('')
    setVerifying(true)
    try {
      const res = await apiFetch('/api/auth/verify-email', {
        method: 'POST',
        auth: false,
        body: JSON.stringify({ email: form.email, code }),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || 'Verification failed')
      localStorage.setItem('token', data.access_token)
      window.location.href = '/'
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al verificar')
    }
    setVerifying(false)
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
          <div className="auth-header">
            <img src="/logo.png" alt="Mimetic AI" className="auth-logo" />
          </div>

        {step === 'form' ? (
          <form onSubmit={handleSubmit}>
            <h2>Registro de paciente</h2>
            <p className="auth-hint">Completa todos tus datos para crear tu historial médico</p>
            {error && <div className="auth-error">{error}</div>}

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
              <input type="email" placeholder="paciente@correo.com" value={form.email} onChange={set('email')} required />
            </div>

            <div className="auth-field">
              <label>Teléfono de contacto</label>
              <input type="tel" placeholder="Ej: 3001234567" value={form.phone} onChange={set('phone')} required />
            </div>

            <div className="auth-row auth-row-3">
              <div className="auth-field">
                <label>País</label>
                <select value={form.country} onChange={handleCountryChange} required>
                  <option value="" disabled>Selecciona un país</option>
                  {countries.map(c => (
                    <option key={c.code} value={c.code}>{c.name}</option>
                  ))}
                </select>
              </div>
              <div className="auth-field">
                <label>Departamento</label>
                <select value={form.department} onChange={handleDepartmentChange} required disabled={departments.length === 0}>
                  <option value="" disabled>
                    {departments.length === 0 ? 'Selecciona un país' : 'Selecciona un departamento'}
                  </option>
                  {departments.map(d => (
                    <option key={d.code} value={d.code}>{d.name}</option>
                  ))}
                </select>
              </div>
              <div className="auth-field">
                <label>Ciudad</label>
                <select value={form.city} onChange={set('city')} required disabled={cities.length === 0}>
                  <option value="" disabled>
                    {loadingCities
                      ? 'Cargando ciudades...'
                      : cities.length === 0
                        ? 'Selecciona un departamento'
                        : 'Selecciona una ciudad'}
                  </option>
                  {cities.map(c => (
                    <option key={c.code} value={c.code}>{c.name}</option>
                  ))}
                </select>
              </div>
            </div>

            <div className="auth-field">
              <label>Contraseña</label>
              <input type="password" placeholder="Mínimo 6 caracteres" value={form.password} onChange={set('password')} required minLength={6} />
            </div>

            <button type="submit" className="auth-btn" disabled={submitting}>
              {submitting ? 'Enviando...' : 'Crear cuenta'}
            </button>
          </form>
        ) : (
          <form onSubmit={handleVerify}>
            <h2>Verifica tu correo</h2>
            <p className="auth-hint">
              Hemos enviado un código de verificación a <strong>{form.email}</strong>
            </p>
            {error && <div className="auth-error">{error}</div>}
            <div className="auth-field">
              <label>Código de verificación</label>
              <input
                type="text"
                placeholder="Ingresa el código de 6 dígitos"
                value={code}
                onChange={e => setCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
                required
                maxLength={6}
              />
            </div>
            <button type="submit" className="auth-btn" disabled={verifying || code.length !== 6}>
              {verifying ? 'Verificando...' : 'Verificar'}
            </button>
          </form>
        )}

        <p className="auth-footer">
          ¿Ya tienes cuenta? <Link to="/login">Inicia sesión</Link>
        </p>
        {step === 'form' && (
          <p className="auth-footer">
            ¿Eres personal del hospital? Solicita tu cuenta al administrador
          </p>
        )}
      </div>
    </div>
  )
}
