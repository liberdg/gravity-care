import { useCallback, useEffect, useState } from 'react'
import { api } from './api.js'
import { STATUS_LABELS } from './utils.js'

const REFRESH_MS = 5000 // les mesures arrivent seules : on recharge régulièrement

export default function Dashboard({ day, onOpen }) {
  const [rows, setRows] = useState(null)
  const [error, setError] = useState(null)

  const load = useCallback(async () => {
    try {
      const list = await api.astronauts()
      const data = await Promise.all(list.map((a) => api.status(a.id, day).then((s) => ({ ...a, ...s }))))
      setRows(data)
      setError(null)
    } catch (e) {
      setError(e.message)
    }
  }, [day])

  useEffect(() => {
    load()
    const t = setInterval(load, REFRESH_MS)
    return () => clearInterval(t)
  }, [load])

  if (!rows) return error ? <p className="error">Impossible de charger les données : {error}</p> : <p>Chargement…</p>

  return (
    <section>
      <h2>Équipage</h2>
      {error && <p className="error">Mise à jour impossible ({error}). Dernières données affichées.</p>}
      <div className="cards">
        {rows.map((a) => (
          <button key={a.id} className={`card status-${a.status}`} onClick={() => onOpen(a.id)}>
            <span className="card-title">{a.alias}</span>
            <span className="card-role">{a.mission_role}</span>
            <span className={`badge status-${a.status}`}>{STATUS_LABELS[a.status]}</span>
            <span className="card-count">
              {a.reasons.length === 0 ? 'Aucune alerte' : `${a.reasons.length} indicateur(s) en écart`}
            </span>
            {a.sensor_silent && (
              <span className="silent">Capteurs silencieux depuis {Math.round(a.silent_hours)} h</span>
            )}
          </button>
        ))}
      </div>
      <p className="hint">Les mesures sont envoyées automatiquement par les capteurs (simulés). Mise à jour toutes les 5 secondes.</p>
    </section>
  )
}
