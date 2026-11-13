import { useCallback, useEffect, useState } from 'react'
import { api } from './api.js'
import { AstronautAvatar, Icon } from './Art.jsx'
import SimPanel from './SimPanel.jsx'
import { STATUS_LABELS } from './utils.js'

export default function Dashboard({ day, role }) {
  const [rows, setRows] = useState(null)
  const [error, setError] = useState(null)
  const [running, setRunning] = useState(false)
  const canSimulate = role === 'medecin' || role === 'responsable'

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
    const t = setInterval(load, running ? 1500 : 5000)
    return () => clearInterval(t)
  }, [load, running])

  const noData = rows && rows.every((a) => a.last_day == null)
  const counts = rows ? ['vert', 'orange', 'rouge', 'calibration'].map((s) => [s, rows.filter((a) => a.status === s).length]) : []

  return (
    <section className="page">
      <h1>Tableau de bord de l'équipage</h1>
      {canSimulate && <SimPanel onProgress={(s) => setRunning(!!s.running)} />}

      {!rows && (error ? <p className="error">Impossible de charger les données : {error}</p> : <p>Chargement…</p>)}
      {error && rows && <p className="error">Mise à jour impossible ({error}). Dernières données affichées.</p>}

      {rows && noData && (
        <div className="empty">
          <Icon name="sensor" size={34} />
          <h3>Aucune mesure reçue pour le moment</h3>
          <p>{canSimulate ? 'Cliquez sur « Lancer la simulation des capteurs » ci-dessus : le tableau de bord se remplira tout seul.'
                           : 'Demandez au médecin ou au responsable de lancer la simulation des capteurs.'}</p>
        </div>
      )}

      {rows && !noData && (
        <>
          <div className="kpis">
            {counts.map(([s, n]) => (
              <div key={s} className={`kpi status-${s}`}><span className="kpi-n">{n}</span><span>{STATUS_LABELS[s]}</span></div>
            ))}
          </div>
          <div className="cards">
            {rows.map((a) => (
              <a key={a.id} href={`#/dashboard/${a.id}`} className={`card status-${a.status}`}>
                <div className="card-top">
                  <AstronautAvatar code={a.code} status={a.status} size={64} />
                  <div>
                    <span className="card-title">{a.alias}</span>
                    <span className="card-role">{a.mission_role}</span>
                  </div>
                </div>
                <span className={`badge status-${a.status}`}>{STATUS_LABELS[a.status]}</span>
                <span className="card-count">
                  {a.reasons.length === 0 ? 'Aucune alerte' : `${a.reasons.length} indicateur(s) en écart`}
                  {a.last_day ? ` · jour ${a.last_day}` : ''}
                </span>
                {a.sensor_silent && <span className="silent">Capteurs silencieux depuis {Math.round(a.silent_hours)} h</span>}
              </a>
            ))}
          </div>
          <p className="small">Les mesures arrivent automatiquement des capteurs (simulés). Cliquez sur un astronaute pour le détail.</p>
        </>
      )}
    </section>
  )
}
