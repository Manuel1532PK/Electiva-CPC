import { useRef, useState, type FormEvent, type ChangeEvent } from 'react'
import { apiFetch } from '../../api/client'

type Collection = 'symptoms' | 'diseases' | 'treatments'

const COLLECTIONS: { value: Collection; label: string; key: string; columns: string }[] = [
  {
    value: 'symptoms',
    label: 'Síntomas',
    key: 'name',
    columns: 'name, description, category',
  },
  {
    value: 'diseases',
    label: 'Enfermedades',
    key: 'name',
    columns: 'name, description, severity, symptoms (separados por | )',
  },
  {
    value: 'treatments',
    label: 'Tratamientos',
    key: 'disease_name',
    columns: 'disease_name, general_recommendations',
  },
]

type Result = {
  collection: string
  file: string
  detected: number
  inserted: number
  updated: number
  errors: { index: number; reason: string }[]
}

export default function ExpertSystemImport() {
  const [collection, setCollection] = useState<Collection>('symptoms')
  const [file, setFile] = useState<File | null>(null)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [result, setResult] = useState<Result | null>(null)
  const [loading, setLoading] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)

  const current = COLLECTIONS.find(c => c.value === collection)

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    setError('')
    setSuccess('')
    setResult(null)
    setFile(e.target.files?.[0] || null)
  }

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError('')
    setSuccess('')
    setResult(null)

    if (!file) {
      setError('Selecciona un archivo primero')
      return
    }

    setLoading(true)
    try {
      const form = new FormData()
      form.append('file', file)
      form.append('collection', collection)

      const res = await apiFetch('/api/knowledge/import-file', {
        method: 'POST',
        body: form,
      })

      const data = await res.json().catch(() => ({}))
      if (!res.ok) {
        setError(data.detail || 'Error al importar el archivo')
        return
      }
      setResult(data)
      setSuccess(`Importación completada: ${data.inserted} nuevos, ${data.updated} actualizados`)
      setFile(null)
      if (inputRef.current) inputRef.current.value = ''
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al importar')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="admin-card">
      <h3>Importar a la base de conocimiento</h3>
      <p className="admin-hint">
        Alimenta la base de datos de MongoDB Atlas (colección {current?.value}) con un
        archivo <strong>CSV</strong>, <strong>Excel (.xlsx)</strong> o <strong>JSON</strong>.
        Los datos se insertan o actualizan de forma idempotente según la clave{' '}
        <code>{current?.key}</code>.
      </p>

      {error && <div className="auth-error">{error}</div>}
      {success && <div className="auth-success">{success}</div>}

      <form onSubmit={handleSubmit}>
        <div className="auth-field">
          <label>Tipo de datos</label>
          <select
            value={collection}
            onChange={e => setCollection(e.target.value as Collection)}
          >
            {COLLECTIONS.map(c => (
              <option key={c.value} value={c.value}>
                {c.label}
              </option>
            ))}
          </select>
        </div>

        <div className="auth-field">
          <label>Archivo (CSV, XLSX o JSON)</label>
          <input
            ref={inputRef}
            type="file"
            accept=".csv,.txt,.json,.xlsx,.xls"
            onChange={handleFileChange}
          />
          <p className="admin-hint">
            Columnas esperadas: <code>{current?.columns}</code>
          </p>
        </div>

        <button className="auth-btn" type="submit" disabled={loading || !file}>
          {loading ? 'Importando...' : 'Importar'}
        </button>
      </form>

      {result && (
        <div className="admin-result">
          <div className="admin-result-grid">
            <div className="admin-result-item">
              <span className="admin-result-value">{result.detected}</span>
              <span className="admin-result-label">Detectados</span>
            </div>
            <div className="admin-result-item">
              <span className="admin-result-value">{result.inserted}</span>
              <span className="admin-result-label">Insertados</span>
            </div>
            <div className="admin-result-item">
              <span className="admin-result-value">{result.updated}</span>
              <span className="admin-result-label">Actualizados</span>
            </div>
            <div className="admin-result-item">
              <span className="admin-result-value">{result.errors.length}</span>
              <span className="admin-result-label">Errores</span>
            </div>
          </div>

          {result.errors.length > 0 && (
            <div className="admin-table-wrap">
              <table className="admin-table">
                <thead>
                  <tr>
                    <th>#</th>
                    <th>Motivo</th>
                  </tr>
                </thead>
                <tbody>
                  {result.errors.slice(0, 20).map((err, i) => (
                    <tr key={i}>
                      <td>{err.index}</td>
                      <td>{err.reason}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
