import { useCallback, useEffect, useState } from 'react'
import { CartesianGrid, Line, LineChart, ReferenceArea, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { api } from './api.js'
import { buildChartData, formatDateTime, INDICATORS, STATUS_LABELS } from './utils.js'

const REFRESH_MS = 5000

function Chart({ indicator, points, forecast, baselineDays, alertLevel }) {
  const color = alertLevel === 'rouge' ? '#d64545' : alertLevel === 'orange' ? '#e08a1e' : '#3b82f6'
  const data = buildChartData(points, forecast)
  return (
    <div className="chart">
      <h3>
        {indicator.label} <small>({indicator.unit})</small>
        {alertLevel && <span className={`badge status-${alertLevel}`}>{STATUS_LABELS[alertLevel]}</span>}
      </h3>
      <ResponsiveContainer width="100%" height={180}>
        <LineChart data={data} margin={{ top: 5, right: 10, left: -15, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2a3446" />
          <XAxis dataKey="day" tick={{ fontSize: 11 }} />
          <YAxis domain={['auto', 'auto']} tick={{ fontSize: 11 }} />
          <Tooltip
            formatter={(v, name) => [`${Number(v).toFixed(2)} ${indicator.unit}`, name === 'forecast' ? 'Prévision' : 'Valeur du jour']}
            labelFormatter={(d) => `Jour ${d}`}
          />
          <ReferenceArea x1={1} x2={baselineDays} fill="#64748b" fillOpacity={0.18} />
          <Line type="monotone" dataKey="value" stroke={color} strokeWidth={2} dot={{ r: 2 }} isAnimationActive={false} connectNulls />
          <Line type="monotone" dataKey="forecast" stroke="#a78bfa" strokeWidth={2} strokeDasharray="5 4" dot={false} isAnimationActive={false} connectNulls />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}

export default function AstronautPage({ id, day, role, onBack }) {
  const [astro, setAstro] = useState(null)
  const [daily, setDaily] = useState({})
  const [status, setStatus] = useState(null)
  const [forecast, setForecast] = useState({ forecast: {}, warning: '' })
  const [alerts, setAlerts] = useState([])
  const [notes, setNotes] = useState([])
  const [text, setText] = useState('')
  const [error, setError] = useState(null)
  const isDoctor = role === 'medecin'

  const load = useCallback(async () => {
    try {
      const [a, d, s, f, al] = await Promise.all([
        api.astronaut(id), api.daily(id, day), api.status(id, day), api.forecast(id, day), api.alerts(id),
      ])
      setAstro(a); setDaily(d); setStatus(s); setForecast(f); setAlerts(al)
      if (isDoctor) setNotes(await api.notes(id))
      setError(null)
    } catch (e) {
      setError(e.message)
    }
  }, [id, day, isDoctor])

  useEffect(() => {
    load()
    const t = setInterval(load, REFRESH_MS)
    return () => clearInterval(t)
  }, [load])

  async function submitNote(e) {
    e.preventDefault()
    if (!text.trim()) return
    try {
      const n = await api.addNote(id, text.trim())
      setNotes((prev) => [...prev, n])
      setText('')
    } catch (err) {
      setError(err.message)
    }
  }

  async function acknowledge(alertId) {
    try {
      const updated = await api.ack(alertId)
      setAlerts((prev) => prev.map((a) => (a.id === updated.id ? updated : a)))
    } catch (err) {
      setError(err.message)
    }
  }

  async function exportReport() {
    try {
      const blob = await api.report(id, day)
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `rapport-${astro.code}-jour-${day}.html`
      a.click()
      URL.revokeObjectURL(url)
    } catch (err) {
      setError(err.message)
    }
  }

  if (!astro || !status) return error ? <p className="error">Erreur : {error}</p> : <p>Chargement…</p>

  const levelByIndicator = Object.fromEntries(status.reasons.map((r) => [r.indicator, r.level]))
  const canAck = role === 'astronaute' || isDoctor

  return (
    <section>
      {onBack && <button className="link" onClick={onBack}>← Équipage</button>}
      <h2>
        {astro.alias} <small>{astro.mission_role}</small>
        <span className={`badge status-${status.status}`}>{STATUS_LABELS[status.status]}</span>
        {isDoctor && <button className="export" onClick={exportReport}>Exporter le rapport</button>}
      </h2>
      {error && <p className="error">Mise à jour impossible ({error}). Dernières données affichées.</p>}
      <p className="hint">
        Jour de mission {day} · Dernière mesure reçue : {formatDateTime(status.last_reading_at)}. La zone grise est la
        période de référence ({astro.baseline_days} premiers jours) qui sert de ligne de base personnelle.
      </p>
      {status.sensor_silent && (
        <p className="alert status-orange silent-box">
          Capteurs silencieux depuis environ {Math.round(status.silent_hours)} h : aucune mesure récente pour cet astronaute.
        </p>
      )}

      <h3>Alertes (état au jour {day})</h3>
      {status.reasons.length === 0 ? (
        <p>{status.status === 'calibration' ? 'Calibration en cours : pas encore assez de données.' : 'Aucun écart détecté.'}</p>
      ) : (
        <ul className="alerts">
          {status.reasons.map((r) => (
            <li key={r.indicator} className={`alert status-${r.level}`}>
              <span className={`badge status-${r.level}`}>{STATUS_LABELS[r.level]}</span> {r.explanation}
              <div className="reco">{r.recommendation}</div>
            </li>
          ))}
        </ul>
      )}

      {alerts.length > 0 && (
        <>
          <h3>Alertes enregistrées</h3>
          <ul className="alerts">
            {alerts.map((a) => (
              <li key={a.id} className={`alert status-${a.level}`}>
                <span className={`badge status-${a.level}`}>{STATUS_LABELS[a.level]}</span>{' '}
                {INDICATORS.find((i) => i.key === a.indicator)?.label || a.indicator}
                {a.acknowledged ? (
                  <span className="acked"> · acquittée</span>
                ) : (
                  canAck && <button className="ack" onClick={() => acknowledge(a.id)}>Accuser réception</button>
                )}
              </li>
            ))}
          </ul>
        </>
      )}

      <div className="charts">
        {INDICATORS.map((ind) => (
          <Chart key={ind.key} indicator={ind} points={daily[ind.key] || []}
                 forecast={forecast.forecast[ind.key] || []}
                 baselineDays={astro.baseline_days} alertLevel={levelByIndicator[ind.key]} />
        ))}
      </div>
      {forecast.warning && <p className="hint">Ligne en pointillé : {forecast.warning}</p>}

      {isDoctor && (
        <>
          <h3>Notes médicales</h3>
          <ul className="notes">
            {notes.length === 0 && <li>Aucune note.</li>}
            {notes.map((n) => (
              <li key={n.id}><strong>{n.author}</strong> · {new Date(n.created_at + 'Z').toLocaleString('fr-FR')}<br />{n.text}</li>
            ))}
          </ul>
          <form onSubmit={submitNote} className="note-form">
            <input value={text} onChange={(e) => setText(e.target.value)} placeholder="Ajouter une note…" maxLength={2000} />
            <button type="submit">Ajouter</button>
          </form>
        </>
      )}
    </section>
  )
}
