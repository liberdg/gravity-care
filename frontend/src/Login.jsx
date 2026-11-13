import { useState } from 'react'
import { api, session } from './api.js'
import { AstronautAvatar } from './Art.jsx'

const DEMO = [
  ['medecin', 'medecin-demo', 'Médecin au sol', 'Tout voir, notes, rapport, simulation'],
  ['responsable', 'responsable-demo', 'Responsable de mission', 'Consulter, simulation'],
  ['astro_b', 'astro-b-demo', 'Astronaute (Astro-B)', 'Son propre suivi'],
]

export default function Login({ onLogin }) {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState(null)
  const [busy, setBusy] = useState(false)

  async function submit(e) {
    e.preventDefault()
    setBusy(true)
    setError(null)
    try {
      const s = await api.login(username, password)
      session.set(s)
      onLogin(s)
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <section className="login page">
      <div className="login-card">
        <AstronautAvatar code="G" status="vert" size={72} />
        <h1>Connexion</h1>
        <p className="small">Accédez au tableau de bord de l'équipage.</p>
        <form onSubmit={submit}>
          <input value={username} onChange={(e) => setUsername(e.target.value)} placeholder="Identifiant" autoComplete="username" />
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Mot de passe" autoComplete="current-password" />
          <button className="btn primary" type="submit" disabled={busy || !username || !password}>Se connecter</button>
        </form>
        {error && <p className="error">{error}</p>}
      </div>
      <div className="login-demo">
        <h3>Comptes de démonstration</h3>
        <p className="small">Cliquez sur un compte pour remplir le formulaire.</p>
        {DEMO.map(([u, p, label, desc]) => (
          <button key={u} className="demo-account" onClick={() => { setUsername(u); setPassword(p) }}>
            <strong>{label}</strong><span>{desc}</span>
          </button>
        ))}
      </div>
    </section>
  )
}
