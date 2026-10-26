import { useState, useEffect } from 'react'
import { useAuth } from '../context/AuthContext'
import {
  getMyClinicalHistory,
  getMySessions,
  getMyTreatments,
  getMySummary,
  type PatientSession,
  type PatientTreatment,
  type PatientSummary,
  type ClinicalHistory,
} from '../api/patient'

type Tab = 'resumen' | 'historial' | 'tratamientos'

const TZ = 'America/Bogota'

function parseDate(dateStr: string): Date {
  const s = dateStr.endsWith('Z') || dateStr.includes('+') ? dateStr : dateStr + 'Z'
  return new Date(s)
}

function formatDate(dateStr: string): string {
  return parseDate(dateStr).toLocaleDateString('es-CO', { day: 'numeric', month: 'long', year: 'numeric', timeZone: TZ })
}

function formatTime(dateStr: string): string {
  return parseDate(dateStr).toLocaleTimeString('es-CO', { hour: '2-digit', minute: '2-digit', timeZone: TZ })
}

function severityColor(sev?: string): string {
  if (!sev) return '#64748b'
  const s = sev.toLowerCase()
  if (s === 'leve' || s === 'low') return '#22c55e'
  if (s === 'moderada' || s === 'medium' || s === 'moderate') return '#eab308'
  if (s === 'severa' || s === 'high' || s === 'severe') return '#ef4444'
  return '#64748b'
}

function severityLabel(sev?: string): string {
  if (!sev) return 'Sin clasificar'
  const s = sev.toLowerCase()
  if (s === 'leve' || s === 'low') return 'Leve'
  if (s === 'moderada' || s === 'medium' || s === 'moderate') return 'Moderada'
  if (s === 'severa' || s === 'high' || s === 'severe') return 'Severa'
  return sev
}

export default function PatientDashboard() {
  const { user, logout } = useAuth()
  const [tab, setTab] = useState<Tab>('resumen')
  const [summary, setSummary] = useState<PatientSummary | null>(null)
  const [sessions, setSessions] = useState<PatientSession[]>([])
  const [treatments, setTreatments] = useState<PatientTreatment[]>([])
  const [clinicalHistory, setClinicalHistory] = useState<ClinicalHistory | null>(null)
  const [loading, setLoading] = useState(true)
  const [expandedSession, setExpandedSession] = useState<string | null>(null)
  const [selectedSession, setSelectedSession] = useState<PatientSession | null>(null)
  const [showDetail, setShowDetail] = useState(false)
  const [loadingDetail, setLoadingDetail] = useState(false)

  useEffect(() => {
    loadData()
  }, [])

  async function loadData() {
    setLoading(true)
    try {
      const [sum, sess, tx, hist] = await Promise.all([
        getMySummary(),
        getMySessions(),
        getMyTreatments(),
        getMyClinicalHistory(),
      ])
      setSummary(sum)
      setSessions(sess)
      setTreatments(tx)
      setClinicalHistory(hist)
    } catch (err) {
      console.error('Error loading patient data:', err)
    } finally {
      setLoading(false)
    }
  }

  async function handleViewDetail(sessionId: string) {
    setLoadingDetail(true)
    setShowDetail(true)
    try {
      const detail = sessions.find(s => s.id === sessionId)
      if (detail) {
        setSelectedSession(detail)
      }
    } finally {
      setLoadingDetail(false)
    }
  }

  function toggleExpand(sessionId: string) {
    setExpandedSession(expandedSession === sessionId ? null : sessionId)
  }

  if (loading) {
    return (
      <div className="app">
        <header className="header">
          <img src="/logo.png" alt="Mimetic AI" className="header-logo-lg" />
          <span className="subtitle">Portal del Paciente</span>
          <div className="header-right">
            <span className="user-badge">{user?.name}</span>
            <button className="logout-btn" onClick={logout}>Cerrar sesión</button>
          </div>
        </header>
        <div className="loading-screen">
          <div className="spinner" />
          <p>Cargando tu información...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="app">
      <header className="header">
        <img src="/logo.png" alt="Mimetic AI" className="header-logo-lg" />
        <span className="subtitle">Portal del Paciente</span>
        <div className="header-right">
          <span className="user-badge">{user?.name}</span>
          <button className="logout-btn" onClick={logout}>Cerrar sesión</button>
        </div>
      </header>

      <div className="pd-welcome">
        <h2>Hola, {user?.first_name || user?.name}</h2>
        <p>Aquí puedes consultar tu información médica de forma sencilla</p>
      </div>

      <div className="pd-tabs">
        <button
          className={`pd-tab ${tab === 'resumen' ? 'active' : ''}`}
          onClick={() => setTab('resumen')}
        >
          Resumen
        </button>
        <button
          className={`pd-tab ${tab === 'historial' ? 'active' : ''}`}
          onClick={() => setTab('historial')}
        >
          Historial de Consultas
        </button>
        <button
          className={`pd-tab ${tab === 'tratamientos' ? 'active' : ''}`}
          onClick={() => setTab('tratamientos')}
        >
          Mis Tratamientos
        </button>
      </div>

      <div className="pd-content">
        {tab === 'resumen' && summary && (
          <ResumenTab summary={summary} clinicalHistory={clinicalHistory} onViewDetail={handleViewDetail} />
        )}
        {tab === 'historial' && (
          <HistorialTab
            sessions={sessions}
            expandedSession={expandedSession}
            onToggleExpand={toggleExpand}
            onViewDetail={handleViewDetail}
          />
        )}
        {tab === 'tratamientos' && (
          <TratamientosTab treatments={treatments} />
        )}
      </div>

      {showDetail && selectedSession && (
        <SessionDetailModal
          session={selectedSession}
          loading={loadingDetail}
          onClose={() => { setShowDetail(false); setSelectedSession(null) }}
        />
      )}
    </div>
  )
}

function ResumenTab({ summary, clinicalHistory, onViewDetail }: {
  summary: PatientSummary
  clinicalHistory: ClinicalHistory | null
  onViewDetail: (id: string) => void
}) {
  return (
    <div className="pd-resumen">
      <div className="pd-stats-grid">
        <div className="pd-stat-card">
          <div className="pd-stat-icon">📋</div>
          <div className="pd-stat-value">{summary.total_sessions}</div>
          <div className="pd-stat-label">Consultas realizadas</div>
        </div>
        <div className="pd-stat-card">
          <div className="pd-stat-icon">🔍</div>
          <div className="pd-stat-value">{summary.total_diagnoses}</div>
          <div className="pd-stat-label">Diagnósticos</div>
        </div>
        <div className="pd-stat-card">
          <div className="pd-stat-icon">🏥</div>
          <div className="pd-stat-value">{summary.hospitals_visited.length}</div>
          <div className="pd-stat-label">Hospitales visitados</div>
        </div>
        <div className="pd-stat-card">
          <div className="pd-stat-icon">📅</div>
          <div className="pd-stat-value">
            {summary.last_session_date ? formatDate(summary.last_session_date) : 'Sin consultas'}
          </div>
          <div className="pd-stat-label">Última consulta</div>
        </div>
      </div>

      {clinicalHistory && (
        <div className="pd-info-card">
          <h3>Mi Información</h3>
          <div className="pd-info-grid">
            <div className="pd-info-item">
              <span className="pd-info-label">Nombre</span>
              <span className="pd-info-value">{clinicalHistory.first_name} {clinicalHistory.last_name}</span>
            </div>
            <div className="pd-info-item">
              <span className="pd-info-label">Documento</span>
              <span className="pd-info-value">{clinicalHistory.document_type} {clinicalHistory.document_number}</span>
            </div>
            <div className="pd-info-item">
              <span className="pd-info-label">Fecha de nacimiento</span>
              <span className="pd-info-value">{clinicalHistory.birth_date || 'No registrado'}</span>
            </div>
            <div className="pd-info-item">
              <span className="pd-info-label">Edad</span>
              <span className="pd-info-value">{clinicalHistory.age ? `${clinicalHistory.age} años` : 'No registrado'}</span>
            </div>
            <div className="pd-info-item">
              <span className="pd-info-label">Género</span>
              <span className="pd-info-value">{clinicalHistory.gender || 'No registrado'}</span>
            </div>
            <div className="pd-info-item">
              <span className="pd-info-label">Teléfono</span>
              <span className="pd-info-value">{clinicalHistory.phone || 'No registrado'}</span>
            </div>
          </div>
        </div>
      )}

      {summary.hospitals_visited.length > 0 && (
        <div className="pd-info-card">
          <h3>Hospitales donde me he atendido</h3>
          <div className="pd-hospital-list">
            {summary.hospitals_visited.map((h, i) => (
              <span key={i} className="pd-hospital-badge">🏥 {h}</span>
            ))}
          </div>
        </div>
      )}

      {summary.recent_sessions.length > 0 && (
        <div className="pd-info-card">
          <h3>Consultas recientes</h3>
          <div className="pd-recent-list">
            {summary.recent_sessions.map(s => (
              <div key={s.id} className="pd-recent-item" onClick={() => onViewDetail(s.id)}>
                <div className="pd-recent-date">{formatDate(s.date)}</div>
                <div className="pd-recent-reason">{s.consultation_reason || 'Sin motivo registrado'}</div>
                <div className="pd-recent-tags">
                  {s.hospital_name && <span className="pd-tag hospital">🏥 {s.hospital_name}</span>}
                  {s.diagnoses.length > 0 && (
                    <span className="pd-tag diagnosis">🩺 {s.diagnoses[0].disease_name}</span>
                  )}
                  {s.has_treatment && <span className="pd-tag treatment">💊 Con tratamiento</span>}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {summary.total_sessions === 0 && (
        <div className="pd-empty">
          <div className="pd-empty-icon">📋</div>
          <h3>Aún no tienes consultas registradas</h3>
          <p>Cuando tu médico realice una consulta, aparecerá aquí tu información.</p>
        </div>
      )}
    </div>
  )
}

function HistorialTab({ sessions, expandedSession, onToggleExpand, onViewDetail }: {
  sessions: PatientSession[]
  expandedSession: string | null
  onToggleExpand: (id: string) => void
  onViewDetail: (id: string) => void
}) {
  if (sessions.length === 0) {
    return (
      <div className="pd-empty">
        <div className="pd-empty-icon">📋</div>
        <h3>No hay consultas registradas</h3>
        <p>Cuando tu médico realice una consulta, aparecerá aquí.</p>
      </div>
    )
  }

  return (
    <div className="pd-timeline">
      {sessions.map((session) => (
        <div key={session.id} className={`pd-timeline-item ${expandedSession === session.id ? 'expanded' : ''}`}>
          <div className="pd-timeline-dot" />
          <div className="pd-timeline-card">
            <div className="pd-timeline-header" onClick={() => onToggleExpand(session.id)}>
              <div className="pd-timeline-date">
                <span className="pd-date-day">{parseDate(session.date).toLocaleDateString('es-CO', { day: 'numeric', timeZone: TZ })}</span>
                <span className="pd-date-month">{parseDate(session.date).toLocaleDateString('es-CO', { month: 'short', timeZone: TZ })}</span>
                <span className="pd-date-year">{parseDate(session.date).toLocaleDateString('es-CO', { year: 'numeric', timeZone: TZ })}</span>
              </div>
              <div className="pd-timeline-info">
                <div className="pd-timeline-reason">{session.consultation_reason || 'Consulta médica'}</div>
                <div className="pd-timeline-meta">
                  {session.hospital_name && <span>🏥 {session.hospital_name}</span>}
                  {session.doctor_name && <span>👨‍⚕️ Dr. {session.doctor_name}</span>}
                </div>
              </div>
              <div className="pd-timeline-badges">
                {session.diagnoses.length > 0 && (
                  <span className="pd-badge diagnosis">{session.diagnoses.length} diagnóstico{session.diagnoses.length > 1 ? 's' : ''}</span>
                )}
                {session.symptoms.length > 0 && (
                  <span className="pd-badge symptom">{session.symptoms.length} síntoma{session.symptoms.length > 1 ? 's' : ''}</span>
                )}
                {session.treatment && <span className="pd-badge treatment">💊 Tratamiento</span>}
              </div>
              <span className="pd-expand-icon">{expandedSession === session.id ? '▲' : '▼'}</span>
            </div>

            {expandedSession === session.id && (
              <div className="pd-timeline-details">
                {session.consultation_reason && (
                  <div className="pd-detail-section">
                    <h4>Motivo de la consulta</h4>
                    <p>{session.consultation_reason}</p>
                  </div>
                )}

                {session.symptom_evolution && (
                  <div className="pd-detail-section">
                    <h4>Cómo evolucionaron los síntomas</h4>
                    <p>{session.symptom_evolution}</p>
                  </div>
                )}

                {session.symptoms.length > 0 && (
                  <div className="pd-detail-section">
                    <h4>Síntomas que presentaste</h4>
                    <div className="pd-symptom-list">
                      {session.symptoms.map((s, i) => (
                        <span key={i} className="pd-symptom-chip">{s}</span>
                      ))}
                    </div>
                  </div>
                )}

                {session.diagnoses.length > 0 && (
                  <div className="pd-detail-section">
                    <h4>Diagnósticos</h4>
                    {session.diagnoses.map((d, i) => (
                      <div key={i} className="pd-diagnosis-card">
                        <div className="pd-diagnosis-header">
                          <span className="pd-diagnosis-name">{d.disease_name}</span>
                          {d.severity && (
                            <span className="pd-severity" style={{ background: severityColor(d.severity) }}>
                              {severityLabel(d.severity)}
                            </span>
                          )}
                        </div>
                        {d.description && <p className="pd-diagnosis-desc">{d.description}</p>}
                      </div>
                    ))}
                  </div>
                )}

                {session.allergies && (
                  <div className="pd-detail-section">
                    <h4>Alergias conocidas</h4>
                    <p className="pd-alert">{session.allergies}</p>
                  </div>
                )}

                {(session.blood_pressure || session.heart_rate || session.temperature || session.weight) && (
                  <div className="pd-detail-section">
                    <h4>Signos vitales</h4>
                    <div className="pd-vitals-grid">
                      {session.blood_pressure && <div className="pd-vital"><span className="pd-vital-label">Presión arterial</span><span className="pd-vital-value">{session.blood_pressure} mmHg</span></div>}
                      {session.heart_rate && <div className="pd-vital"><span className="pd-vital-label">Frecuencia cardíaca</span><span className="pd-vital-value">{session.heart_rate} lpm</span></div>}
                      {session.temperature && <div className="pd-vital"><span className="pd-vital-label">Temperatura</span><span className="pd-vital-value">{session.temperature} °C</span></div>}
                      {session.weight && <div className="pd-vital"><span className="pd-vital-label">Peso</span><span className="pd-vital-value">{session.weight} kg</span></div>}
                      {session.height && <div className="pd-vital"><span className="pd-vital-label">Estatura</span><span className="pd-vital-value">{session.height} cm</span></div>}
                    </div>
                  </div>
                )}

                {session.treatment && (
                  <div className="pd-detail-section">
                    <h4>Tratamiento indicado</h4>
                    <TreatmentMini treatment={session.treatment} />
                  </div>
                )}

                <div className="pd-detail-actions">
                  <button className="pd-btn primary" onClick={() => onViewDetail(session.id)}>
                    Ver reporte completo
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  )
}

function TreatmentMini({ treatment }: {
  treatment: NonNullable<PatientSession['treatment']>
}) {
  const meds = treatment.available || treatment.medicines || []
  return (
    <div className="pd-treatment-mini">
      {treatment.disease_name && (
        <div className="pd-treatment-disease">Para: <strong>{treatment.disease_name}</strong></div>
      )}
      {meds.length > 0 ? (
        <div className="pd-meds-list">
          {meds.map((m, i) => (
            <div key={i} className="pd-med-item">
              <span className="pd-med-name">{m.name}</span>
              {m.dosage && <span className="pd-med-detail">{m.dosage}</span>}
              {m.frequency && <span className="pd-med-detail">{m.frequency}</span>}
            </div>
          ))}
        </div>
      ) : (
        <p className="pd-no-meds">No se indicaron medicamentos</p>
      )}
      {treatment.general_recommendations && (
        <div className="pd-recommendations">
          <strong>Recomendaciones:</strong>
          <p>{treatment.general_recommendations}</p>
        </div>
      )}
    </div>
  )
}

function TratamientosTab({ treatments }: { treatments: PatientTreatment[] }) {
  if (treatments.length === 0) {
    return (
      <div className="pd-empty">
        <div className="pd-empty-icon">💊</div>
        <h3>No tienes tratamientos registrados</h3>
        <p>Cuando tu médico te indique un tratamiento, aparecerá aquí con instrucciones claras.</p>
      </div>
    )
  }

  return (
    <div className="pd-treatments">
      {treatments.map((tx, idx) => (
        <div key={idx} className="pd-treatment-card">
          <div className="pd-treatment-header">
            <div>
              <h3>{tx.disease_name}</h3>
              <div className="pd-treatment-meta">
                <span>📅 {formatDate(tx.session_date)}</span>
                {tx.hospital_name && <span>🏥 {tx.hospital_name}</span>}
              </div>
            </div>
          </div>

          <div className="pd-treatment-body">
            {tx.medicines.length > 0 ? (
              <div className="pd-meds-table">
                <h4>Medicamentos que debes tomar</h4>
                {tx.medicines.map((m, i) => (
                  <div key={i} className="pd-med-card">
                    <div className="pd-med-main">
                      <span className="pd-med-name">{m.name}</span>
                      {m.patient_summary && (
                        <span className="pd-med-summary">{m.patient_summary}</span>
                      )}
                    </div>
                    <div className="pd-med-details">
                      {m.dosage && (
                        <div className="pd-med-field">
                          <span className="pd-med-field-label">Dosis</span>
                          <span className="pd-med-field-value">{m.dosage}</span>
                        </div>
                      )}
                      {m.frequency && (
                        <div className="pd-med-field">
                          <span className="pd-med-field-label">Frecuencia</span>
                          <span className="pd-med-field-value">{m.frequency}</span>
                        </div>
                      )}
                      {m.duration && (
                        <div className="pd-med-field">
                          <span className="pd-med-field-label">Duración</span>
                          <span className="pd-med-field-value">{m.duration}</span>
                        </div>
                      )}
                      {m.route && (
                        <div className="pd-med-field">
                          <span className="pd-med-field-label">Vía</span>
                          <span className="pd-med-field-value">{m.route}</span>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="pd-no-meds">No se indicaron medicamentos para este diagnóstico</p>
            )}

            {tx.general_recommendations && (
              <div className="pd-recommendations-box">
                <h4>Recomendaciones generales</h4>
                <p>{tx.general_recommendations}</p>
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  )
}

function SessionDetailModal({ session, loading, onClose }: {
  session: PatientSession
  loading: boolean
  onClose: () => void
}) {
  return (
    <div className="pd-modal-overlay" onClick={onClose}>
      <div className="pd-modal" onClick={(e) => e.stopPropagation()}>
        <div className="pd-modal-header">
          <h2>Detalle de la Consulta</h2>
          <button className="pd-modal-close" onClick={onClose}>✕</button>
        </div>

        {loading ? (
          <div className="pd-modal-loading">
            <div className="spinner" />
            <p>Cargando detalle...</p>
          </div>
        ) : (
          <div className="pd-modal-body">
            <div className="pd-modal-section">
              <h3>Información de la consulta</h3>
              <div className="pd-modal-grid">
                <div className="pd-modal-field">
                  <span className="pd-modal-label">Fecha</span>
                  <span className="pd-modal-value">{formatDate(session.date)}</span>
                </div>
                <div className="pd-modal-field">
                  <span className="pd-modal-label">Hora</span>
                  <span className="pd-modal-value">{formatTime(session.date)}</span>
                </div>
                <div className="pd-modal-field">
                  <span className="pd-modal-label">Hospital</span>
                  <span className="pd-modal-value">{session.hospital_name || 'No registrado'}</span>
                </div>
                <div className="pd-modal-field">
                  <span className="pd-modal-label">Médico</span>
                  <span className="pd-modal-value">Dr. {session.doctor_name || 'No registrado'}</span>
                </div>
              </div>
            </div>

            {session.consultation_reason && (
              <div className="pd-modal-section">
                <h3>Motivo de consulta</h3>
                <p>{session.consultation_reason}</p>
              </div>
            )}

            {session.symptoms.length > 0 && (
              <div className="pd-modal-section">
                <h3>Síntomas</h3>
                <div className="pd-symptom-list">
                  {session.symptoms.map((s, i) => (
                    <span key={i} className="pd-symptom-chip">{s}</span>
                  ))}
                </div>
              </div>
            )}

            {session.diagnoses.length > 0 && (
              <div className="pd-modal-section">
                <h3>Diagnósticos</h3>
                {session.diagnoses.map((d, i) => (
                  <div key={i} className="pd-diagnosis-card">
                    <div className="pd-diagnosis-header">
                      <span className="pd-diagnosis-name">{d.disease_name}</span>
                      {d.severity && (
                        <span className="pd-severity" style={{ background: severityColor(d.severity) }}>
                          {severityLabel(d.severity)}
                        </span>
                      )}
                    </div>
                    {d.description && <p className="pd-diagnosis-desc">{d.description}</p>}
                  </div>
                ))}
              </div>
            )}

            {session.treatment && (
              <div className="pd-modal-section">
                <h3>Tratamiento</h3>
                <TreatmentMini treatment={session.treatment} />
              </div>
            )}

            {(session.blood_pressure || session.heart_rate || session.temperature || session.weight) && (
              <div className="pd-modal-section">
                <h3>Signos vitales</h3>
                <div className="pd-vitals-grid">
                  {session.blood_pressure && <div className="pd-vital"><span className="pd-vital-label">Presión arterial</span><span className="pd-vital-value">{session.blood_pressure} mmHg</span></div>}
                  {session.heart_rate && <div className="pd-vital"><span className="pd-vital-label">Frecuencia cardíaca</span><span className="pd-vital-value">{session.heart_rate} lpm</span></div>}
                  {session.temperature && <div className="pd-vital"><span className="pd-vital-label">Temperatura</span><span className="pd-vital-value">{session.temperature} °C</span></div>}
                  {session.weight && <div className="pd-vital"><span className="pd-vital-label">Peso</span><span className="pd-vital-value">{session.weight} kg</span></div>}
                  {session.height && <div className="pd-vital"><span className="pd-vital-label">Estatura</span><span className="pd-vital-value">{session.height} cm</span></div>}
                </div>
              </div>
            )}

            {session.allergies && (
              <div className="pd-modal-section">
                <h3>Alergias conocidas</h3>
                <p className="pd-alert">{session.allergies}</p>
              </div>
            )}

            {session.medical_history && (
              <div className="pd-modal-section">
                <h3>Antecedentes médicos</h3>
                <p>{session.medical_history}</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
