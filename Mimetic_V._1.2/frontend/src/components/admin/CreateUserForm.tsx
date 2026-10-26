import { useState, type FormEvent } from 'react'
import { apiFetch } from '../../api/client'

type Hospital = {
  id: string
  name: string
  code: string
}

type Props = {
  isSuperAdmin: boolean
  hospitals: Hospital[]
  onCreated: () => void
}

export default function CreateUserForm({ isSuperAdmin, hospitals, onCreated }: Props) {
  const [email, setEmail] = useState('')
  const [name, setName] = useState('')
  const [password, setPassword] = useState('')
  const [role, setRole] = useState('medico')
  const [hospitalId, setHospitalId] = useState(hospitals[0]?.id || '')
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [loading, setLoading] = useState(false)

  const roleOptions = isSuperAdmin
    ? ['super_admin', 'admin', 'medico', 'paciente']
    : ['medico', 'paciente']

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError('')
    setSuccess('')

    if (password.length < 6) {
      setError('La contraseña debe tener al menos 6 caracteres')
      return
    }

    setLoading(true)
    try {
      const body: Record<string, string> = { email, name, password, role }
      if (!isSuperAdmin || role !== 'super_admin') {
        if (!hospitalId) {
          setError('Debes seleccionar un hospital')
          setLoading(false)
          return
        }
        body.hospital_id = hospitalId
      }

      const res = await apiFetch('/api/auth/create-user', {
        method: 'POST',
        body: JSON.stringify(body),
      })

      const data = await res.json().catch(() => ({}))
      if (!res.ok) {
        setError(data.detail || 'Error al crear el usuario')
        return
      }

      setSuccess(`Usuario creado: ${data.email} (${data.role})`)
      setEmail('')
      setName('')
      setPassword('')
      setRole('medico')
      onCreated()
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="admin-card">
      <h3>Crear usuario</h3>

      {error && <div className="auth-error">{error}</div>}
      {success && <div className="auth-success">{success}</div>}

      <form onSubmit={handleSubmit}>
        {isSuperAdmin && (
          <div className="auth-field">
            <label>Rol</label>
            <select value={role} onChange={e => setRole(e.target.value)}>
              {roleOptions.map(r => (
                <option key={r} value={r}>{r}</option>
              ))}
            </select>
          </div>
        )}

        <div className="auth-field">
          <label>Nombre completo</label>
          <input type="text" value={name} onChange={e => setName(e.target.value)} required />
        </div>

        <div className="auth-field">
          <label>Email</label>
          <input type="email" value={email} onChange={e => setEmail(e.target.value)} required />
        </div>

        <div className="auth-field">
          <label>Contraseña temporal</label>
          <input type="password" value={password} onChange={e => setPassword(e.target.value)} required />
        </div>

        {isSuperAdmin && role !== 'super_admin' && (
          <div className="auth-field">
            <label>Hospital</label>
            <select value={hospitalId} onChange={e => setHospitalId(e.target.value)} required>
              <option value="">Selecciona un hospital</option>
              {hospitals.map(h => (
                <option key={h.id} value={h.id}>{h.name} ({h.code})</option>
              ))}
            </select>
          </div>
        )}

        {!isSuperAdmin && (
          <div className="auth-field">
            <label>Rol</label>
            <select value={role} onChange={e => setRole(e.target.value)}>
              {roleOptions.map(r => (
                <option key={r} value={r}>{r}</option>
              ))}
            </select>
          </div>
        )}

        <button className="auth-btn" type="submit" disabled={loading}>
          {loading ? 'Creando...' : 'Crear usuario'}
        </button>
      </form>
    </div>
  )
}