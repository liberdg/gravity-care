import { useEffect, useState } from 'react'
import { session } from './api.js'
import Login from './Login.jsx'
import Dashboard from './Dashboard.jsx'
import AstronautPage from './AstronautPage.jsx'
import { ROLE_LABELS } from './utils.js'

export default function App() {
  const [me, setMe] = useState(session.get())
  const [selected, setSelected] = useState(null)
  const [day, setDay] = useState(30) // jour de mission affiché (rejoue la démo)
  const [online, setOnline] = useState(navigator.onLine)

  useEffect(() => {
    const out = () => { setMe(null); setSelected(null) }
    const on = () => setOnline(true)
    const off = () => setOnline(false)
    window.addEventListener('gc-logout', out)
    window.addEventListener('online', on)
    window.addEventListener('offline', off)
    return () => {
      window.removeEventListener('gc-logout', out)
      window.removeEventListener('online', on)
      window.removeEventListener('offline', off)
    }
  }, [])

  function logout() {
    session.clear()
    setMe(null)
    setSelected(null)
  }

  const isAstronaut = me?.role === 'astronaute'
  const openId = isAstronaut ? me.astronaut_id : selected

  return (
    <div className="app">
      <div className="banner" role="note">
        DONNÉES SIMULÉES · Prototype de hackathon · Pas un dispositif médical · Aucun diagnostic
      </div>
      {!online && (
        <div className="offline" role="status">
          Hors-ligne : vous voyez les dernières données consultées. Les nouvelles mesures arriveront à la reconnexion.
        </div>
      )}
      <header className="header">
        <h1 onClick={() => setSelected(null)} style={{ cursor: 'pointer' }}>GRAVITY CARE</h1>
        {me && (
          <div className="header-right">
            <label className="day-picker">
              Jour de mission : <strong>{day}</strong>
              <input type="range" min="1" max="30" value={day} onChange={(e) => setDay(Number(e.target.value))} />
            </label>
            <span className="who">{me.username} · {ROLE_LABELS[me.role]}</span>
            <button className="link" onClick={logout}>Se déconnecter</button>
          </div>
        )}
      </header>
      <main>
        {!me ? (
          <Login onLogin={setMe} />
        ) : openId ? (
          <AstronautPage key={openId} id={openId} day={day} role={me.role}
                         onBack={isAstronaut ? null : () => setSelected(null)} />
        ) : (
          <Dashboard day={day} onOpen={setSelected} />
        )}
      </main>
    </div>
  )
}
