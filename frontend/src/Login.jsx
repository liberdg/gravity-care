import { useState } from 'react'
import { api, session } from './api.js'

const DEMO = [
  ['medecin', 'medecin-demo', 'Médecin au sol'],
  ['responsable', 'responsable-demo', 'Responsable de mission'],
  ['astro_b', 'astro-b-demo', 'Astronaute (Astro-B)'],
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
    <section className="login">
      <h2>Connexion</h2>
      <form onSubmit={submit}>
        <input value={username} onChange={(e) => setUsername(e.target.value)} placeholder="Identifiant" autoComplete="username" />
        <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Mot de passe" autoComplete="current-password" />
        <button type="submit" disabled={busy || !username || !password}>Se connecter</button>
      </form>
      {error && <p className="error">{error}</p>}
      <div className="hint">
        <p>Comptes de démonstration (cliquez pour remplir) :</p>
        <ul>
          {DEMO.map(([u, p, label]) => (
            <li key={u}><button className="link" onClick={() => { setUsername(u); setPassword(p) }}>{label}</button></li>
          ))}
        </ul>
      </div>
    </section>
  )
}
