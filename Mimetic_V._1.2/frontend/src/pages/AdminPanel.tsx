import { useEffect, useState, type FormEvent } from 'react'
import { useAuth } from '../context/AuthContext'
import { apiFetch } from '../api/client'
import CreateUserForm from '../components/admin/CreateUserForm'
import UserList from '../components/admin/UserList'
import ExpertSystemImport from '../components/admin/ExpertSystemImport'

type Hospital = {
  id: string
  name: string
  code: string
  address: string
  phone: string
  email: string
  active: boolean
  created_at: string
}

export default function AdminPanel() {
  const { user, logout } = useAuth()
  const isSuperAdmin = user?.role === 'super_admin'

  const [tab, setTab] = useState<'users' | 'hospitals' | 'expert'>('users')
  const [hospitals, setHospitals] = useState<Hospital[]>([])
  const [hospError, setHospError] = useState('')
  const [hospLoading, setHospLoading] = useState(false)

  const [newHospital, setNewHospital] = useState({ name: '', code: '', address: '', phone: '', email: '' })
  const [hospMsg, setHospMsg] = useState('')

  const loadHospitals = async () => {
    setHospLoading(true)
    setHospError('')
    try {
      const res = await apiFetch('/api/hospitals')
      if (!res.ok) {
        const data = await res.json().catch(() => ({}))
        throw new Error(data.detail || 'Error al cargar hospitales')
      }
      const data = await res.json()
      setHospitals(data)
    } catch (err) {
      setHospError(err instanceof Error ? err.message : 'Error')
    } finally {
      setHospLoading(false)
    }
  }

  useEffect(() => {
    if (user) {
      loadHospitals()
    }
  }, [user])

  const handleCreateHospital = async (e: FormEvent) => {
    e.preventDefault()
    setHospMsg('')
    setHospError('')
    try {
      const res = await apiFetch('/api/hospitals', {
        method: 'POST',
        body: JSON.stringify(newHospital),
      })
      const data = await res.json().catch(() => ({}))
      if (!res.ok) {
        setHospError(data.detail || 'Error al crear hospital')
        return
      }
      setHospMsg(`Hospital creado: ${data.name} (${data.code})`)
      setNewHospital({ name: '', code: '', address: '', phone: '', email: '' })
      loadHospitals()
    } catch (err) {
      setHospError(err instanceof Error ? err.message : 'Error')
    }
  }

  const toggleHospitalActive = async (h: Hospital) => {
    try {
      const res = await apiFetch(`/api/hospitals/${h.id}`, {
        method: 'PUT',
        body: JSON.stringify({ active: !h.active }),
      })
      if (!res.ok) {
        const data = await res.json().catch(() => ({}))
        throw new Error(data.detail || 'Error al actualizar hospital')
      }
      loadHospitals()
    } catch (err) {
      setHospError(err instanceof Error ? err.message : 'Error')
    }
  }

  return (
    <div className="app">
      <header className="header">
        <img src="/logo.png" alt="Mimetic AI" className="header-logo-lg" />
        <span className="subtitle">Panel de Administración</span>
        <div className="header-right">
          <span className="user-badge">{user?.name}{isSuperAdmin ? ' (Super Admin)' : ''}</span>
          <button className="logout-btn" onClick={logout}>Cerrar sesión</button>
        </div>
      </header>

      <div className="admin-panel">
        <div className="admin-tabs">
          <button
            className={tab === 'users' ? 'admin-tab active' : 'admin-tab'}
            onClick={() => setTab('users')}
          >
            Usuarios
          </button>
          {isSuperAdmin && (
            <button
              className={tab === 'hospitals' ? 'admin-tab active' : 'admin-tab'}
              onClick={() => setTab('hospitals')}
            >
              Hospitales
            </button>
          )}
          {isSuperAdmin && (
            <button
              className={tab === 'expert' ? 'admin-tab active' : 'admin-tab'}
              onClick={() => setTab('expert')}
            >
              Sistema experto
            </button>
          )}
        </div>

        {tab === 'users' && (
          <div className="admin-grid">
            <CreateUserForm
              isSuperAdmin={isSuperAdmin}
              hospitals={hospitals}
              onCreated={() => setTab('users')}
            />
            <UserList isSuperAdmin={isSuperAdmin} hospitals={hospitals} />
          </div>
        )}

        {tab === 'hospitals' && (
          <div className="admin-grid">
            <div className="admin-card">
              <h3>Crear hospital</h3>
              {hospMsg && <div className="auth-success">{hospMsg}</div>}
              {hospError && <div className="auth-error">{hospError}</div>}
              <form onSubmit={handleCreateHospital}>
                <div className="auth-field">
                  <label>Nombre</label>
                  <input
                    type="text"
                    value={newHospital.name}
                    onChange={e => setNewHospital({ ...newHospital, name: e.target.value })}
                    required
                  />
                </div>
                <div className="auth-field">
                  <label>Código (único)</label>
                  <input
                    type="text"
                    value={newHospital.code}
                    onChange={e => setNewHospital({ ...newHospital, code: e.target.value })}
                    placeholder="EJ: HSJ-001"
                    required
                  />
                </div>
                <div className="auth-field">
                  <label>Dirección</label>
                  <input
                    type="text"
                    value={newHospital.address}
                    onChange={e => setNewHospital({ ...newHospital, address: e.target.value })}
                  />
                </div>
                <div className="auth-field">
                  <label>Teléfono</label>
                  <input
                    type="text"
                    value={newHospital.phone}
                    onChange={e => setNewHospital({ ...newHospital, phone: e.target.value })}
                  />
                </div>
                <div className="auth-field">
                  <label>Email</label>
                  <input
                    type="email"
                    value={newHospital.email}
                    onChange={e => setNewHospital({ ...newHospital, email: e.target.value })}
                  />
                </div>
                <button className="auth-btn" type="submit">Crear hospital</button>
              </form>
            </div>

            <div className="admin-card">
              <h3>Hospitales ({hospitals.length})</h3>
              {hospLoading ? (
                <p className="admin-loading">Cargando...</p>
              ) : hospitals.length === 0 ? (
                <p className="admin-empty">No hay hospitales</p>
              ) : (
                <div className="admin-table-wrap">
                  <table className="admin-table">
                    <thead>
                      <tr>
                        <th>Código</th>
                        <th>Nombre</th>
                        <th>Dirección</th>
                        <th>Teléfono</th>
                        <th>Estado</th>
                        <th>Acción</th>
                      </tr>
                    </thead>
                    <tbody>
                      {hospitals.map(h => (
                        <tr key={h.id}>
                          <td>{h.code}</td>
                          <td>{h.name}</td>
                          <td>{h.address || '—'}</td>
                          <td>{h.phone || '—'}</td>
                          <td>{h.active ? 'Activo' : 'Inactivo'}</td>
                          <td>
                            <button
                              className="admin-action-btn"
                              onClick={() => toggleHospitalActive(h)}
                            >
                              {h.active ? 'Desactivar' : 'Activar'}
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        )}

        {tab === 'expert' && isSuperAdmin && (
          <div className="admin-grid">
            <ExpertSystemImport />
          </div>
        )}
      </div>
    </div>
  )
}