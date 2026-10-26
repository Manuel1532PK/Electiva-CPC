import { useEffect, useState } from 'react'
import { apiFetch, errorMessage } from '../../api/client'

type User = {
  id: string
  email: string
  name: string
  role: string
  hospital_id: string
  created_at: string
}

type Hospital = {
  id: string
  name: string
  code: string
}

type Props = {
  isSuperAdmin: boolean
  hospitals: Hospital[]
}

const ROLE_LABELS: Record<string, string> = {
  super_admin: 'Super Admin',
  admin: 'Admin',
  medico: 'Médico',
  paciente: 'Paciente',
}

export default function UserList({ isSuperAdmin, hospitals, }: Props) {
  const [users, setUsers] = useState<User[]>([])
  const [roleFilter, setRoleFilter] = useState('')
  const [hospitalFilter, setHospitalFilter] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const hospitalName = (id: string) => {
    if (!id) return '—'
    const h = hospitals.find(x => x.id === id)
    return h ? h.name : id
  }

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setError('')

    const params = new URLSearchParams()
    if (roleFilter) params.set('role', roleFilter)
    if (isSuperAdmin && hospitalFilter) params.set('hospital_id', hospitalFilter)

    apiFetch('/api/auth/users?' + params.toString())
      .then(async res => {
        if (!res.ok) throw new Error(await errorMessage(res, 'Error al cargar usuarios'))
        return res.json()
      })
      .then(data => {
        if (!cancelled) setUsers(data)
      })
      .catch(err => {
        if (!cancelled) setError(err.message)
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })

    return () => {
      cancelled = true
    }
  }, [roleFilter, hospitalFilter, isSuperAdmin])

  return (
    <div className="admin-card">
      <h3>Usuarios ({users.length})</h3>

      <div className="admin-filters">
        <select value={roleFilter} onChange={e => setRoleFilter(e.target.value)}>
          <option value="">Todos los roles</option>
          {Object.entries(ROLE_LABELS).map(([value, label]) => (
            <option key={value} value={value}>{label}</option>
          ))}
        </select>

        {isSuperAdmin && (
          <select value={hospitalFilter} onChange={e => setHospitalFilter(e.target.value)}>
            <option value="">Todos los hospitales</option>
            {hospitals.map(h => (
              <option key={h.id} value={h.id}>{h.name} ({h.code})</option>
            ))}
          </select>
        )}
      </div>

      {error && <div className="auth-error">{error}</div>}

      {loading ? (
        <p className="admin-loading">Cargando...</p>
      ) : users.length === 0 ? (
        <p className="admin-empty">No hay usuarios</p>
      ) : (
        <div className="admin-table-wrap">
          <table className="admin-table">
            <thead>
              <tr>
                <th>Nombre</th>
                <th>Email</th>
                <th>Rol</th>
                {isSuperAdmin && <th>Hospital</th>}
              </tr>
            </thead>
            <tbody>
              {users.map(u => (
                <tr key={u.id}>
                  <td>{u.name}</td>
                  <td>{u.email}</td>
                  <td>{ROLE_LABELS[u.role] || u.role}</td>
                  {isSuperAdmin && <td>{hospitalName(u.hospital_id)}</td>}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}