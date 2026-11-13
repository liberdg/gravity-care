import { useEffect, useState } from 'react'
import { api } from './api.js'
import { Icon } from './Art.jsx'

const SPEED_LABELS = { lente: 'Lente (≈ 1 min 20)', normale: 'Normale (≈ 30 s)', rapide: 'Rapide (≈ 5 s)' }

// Panneau de simulation des capteurs : remplace le second terminal. Mesures SIMULÉES.
export default function SimPanel({ onProgress }) {
  const [st, setSt] = useState(null)
  const [speed, setSpeed] = useState('normale')
  const [days, setDays] = useState(30)
  const [error, setError] = useState(null)

  useEffect(() => {
    let alive = true
    const tick = async () => {
      try {
        const s = await api.simulation()
        if (alive) { setSt(s); onProgress?.(s) }
      } catch (e) { if (alive) setError(e.message) }
    }
    tick()
    const t = setInterval(tick, st?.running ? 800 : 3000)
    return () => { alive = false; clearInterval(t) }
  }, [st?.running]) // eslint-disable-line react-hooks/exhaustive-deps

  async function start() {
    setError(null)
    try { setSt(await api.startSimulation(speed, days)) } catch (e) { setError(e.message) }
  }
  async function stop() {
    try { setSt(await api.stopSimulation()) } catch (e) { setError(e.message) }
  }

  const running = st?.running
  const pct = Math.round((st?.progress || 0) * 100)

  return (
    <div className="sim">
      <div className="sim-head">
        <div>
          <h3><Icon name="sensor" size={20} /> Simulation des capteurs</h3>
          <p className="small">
            Lance un flux de mesures <strong>simulées</strong> (3 astronautes fictifs). Les données actuelles sont remplacées.
          </p>
        </div>
        <div className="sim-controls">
          <select value={speed} onChange={(e) => setSpeed(e.target.value)} disabled={running} aria-label="Vitesse">
            {Object.entries(SPEED_LABELS).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
          </select>
          <select value={days} onChange={(e) => setDays(Number(e.target.value))} disabled={running} aria-label="Durée">
            {[10, 21, 30].map((d) => <option key={d} value={d}>{d} jours de mission</option>)}
          </select>
          {running ? (
            <button className="btn danger" onClick={stop}><Icon name="stop" size={16} /> Arrêter</button>
          ) : (
            <button className="btn primary" onClick={start}><Icon name="play" size={16} /> Lancer la simulation des capteurs</button>
          )}
        </div>
      </div>
      {(running || st?.finished) && (
        <div className="progress-wrap" aria-label="Progression">
          <div className="progress"><div className="progress-bar" style={{ width: `${pct}%` }} /></div>
          <span className="small">
            {running ? `Jour ${st.day} / ${st.total_days} · ${pct} %` : 'Simulation terminée'}
          </span>
        </div>
      )}
      {(error || st?.error) && <p className="error">{error || st.error}</p>}
    </div>
  )
}
