import { useEffect, useState } from 'react'
import { session } from './api.js'
import { Icon, Logo } from './Art.jsx'
import Landing from './Landing.jsx'
import Method from './Method.jsx'
import Login from './Login.jsx'
import Dashboard from './Dashboard.jsx'
import AstronautPage from './AstronautPage.jsx'
import { parseRoute, ROLE_LABELS } from './utils.js'

export default function App() {
  const [me, setMe] = useState(session.get())
  const [route, setRoute] = useState(parseRoute(window.location.hash))
  const [day, setDay] = useState(30) // jour de mission affiché (rejoue la démo)
  const [online, setOnline] = useState(navigator.onLine)

  useEffect(() => {
    const hash = () => { setRoute(parseRoute(window.location.hash)); window.scrollTo(0, 0) }
    const out = () => setMe(null)
    const on = () => setOnline(true)
    const off = () => setOnline(false)
    window.addEventListener('hashchange', hash)
    window.addEventListener('gc-logout', out)
    window.addEventListener('online', on)
    window.addEventListener('offline', off)
    return () => {
      window.removeEventListener('hashchange', hash)
      window.removeEventListener('gc-logout', out)
      window.removeEventListener('online', on)
      window.removeEventListener('offline', off)
    }
  }, [])

  function logout() {
    session.clear()
    setMe(null)
    window.location.hash = '#/'
  }

  const isAstronaut = me?.role === 'astronaute'
  const inApp = route.page === 'dashboard'
  const openId = isAstronaut ? me.astronaut_id : route.param

  let content
  if (route.page === 'methode') content = <Method />
  else if (inApp) {
    if (!me) content = <Login onLogin={setMe} />
    else if (openId) content = <AstronautPage key={openId} id={openId} day={day} role={me.role} canGoBack={!isAstronaut} />
    else content = <Dashboard day={day} role={me.role} />
  } else content = <Landing />

  return (
    <div className="app">
      <div className="banner" role="note">
        DONNÉES SIMULÉES · Prototype de hackathon · Pas un dispositif médical · Aucun diagnostic
      </div>
      {!online && (
        <div className="offline" role="status">
          <Icon name="offline" size={16} /> Hors-ligne : vous voyez les dernières données consultées.
        </div>
      )}
      <nav className="nav">
        <a className="brand" href="#/"><Logo /> <span>GRAVITY CARE</span></a>
        <div className="nav-links">
          <a href="#/" className={route.page === 'home' ? 'on' : ''}>Accueil</a>
          <a href="#/dashboard" className={inApp ? 'on' : ''}>Tableau de bord</a>
          <a href="#/methode" className={route.page === 'methode' ? 'on' : ''}>Méthode</a>
        </div>
        <div className="nav-right">
          {inApp && me && (
            <label className="day-picker">
              Jour <strong>{day}</strong>
              <input type="range" min="1" max="30" value={day} onChange={(e) => setDay(Number(e.target.value))} aria-label="Jour de mission" />
            </label>
          )}
          {me ? (
            <>
              <span className="who"><Icon name="user" size={15} /> {me.username} · {ROLE_LABELS[me.role]}</span>
              <button className="btn small-btn" onClick={logout}>Se déconnecter</button>
            </>
          ) : (
            <a className="btn small-btn primary" href="#/dashboard">Se connecter</a>
          )}
        </div>
      </nav>
      <main>{content}</main>
    </div>
  )
}
