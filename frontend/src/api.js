// Appels vers le backend. Toute erreur renvoie un message lisible (format {code, message}).
const KEY = 'gc_session'

export const session = {
  get() {
    try { return JSON.parse(localStorage.getItem(KEY)) } catch { return null }
  },
  set(s) { localStorage.setItem(KEY, JSON.stringify(s)) },
  clear() {
    localStorage.removeItem(KEY)
    // Le cache hors-ligne des données ne doit pas survivre à la déconnexion (autre utilisateur possible).
    if (window.caches) caches.delete('gravity-care-api-v1')
  },
}

async function request(path, options = {}) {
  const s = session.get()
  const headers = { ...(options.headers || {}) }
  if (s?.token) headers.Authorization = `Bearer ${s.token}`
  let res
  try {
    res = await fetch(path, { ...options, headers })
  } catch {
    throw new Error('Impossible de joindre le serveur.')
  }
  if (res.status === 401 && s) {
    session.clear()
    window.dispatchEvent(new Event('gc-logout'))
  }
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw new Error(body.message || `Erreur ${res.status}`)
  }
  return options.blob ? res.blob() : res.json()
}

const q = (day) => (day ? `?as_of_day=${day}` : '')

export const api = {
  login: (username, password) =>
    request('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    }),
  astronauts: () => request('/api/astronauts'),
  astronaut: (id) => request(`/api/astronauts/${id}`),
  daily: (id, day) => request(`/api/astronauts/${id}/daily${q(day)}`),
  status: (id, day) => request(`/api/astronauts/${id}/status${q(day)}`),
  forecast: (id, day) => request(`/api/astronauts/${id}/forecast${q(day)}`),
  alerts: (id) => request(`/api/alerts?astronaut_id=${id}`),
  ack: (alertId) => request(`/api/alerts/${alertId}/ack`, { method: 'POST' }),
  notes: (id) => request(`/api/astronauts/${id}/notes`),
  addNote: (id, text) =>
    request(`/api/astronauts/${id}/notes`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text }),
    }),
  simulation: () => request('/api/simulation'),
  startSimulation: (speed, days) =>
    request('/api/simulation/start', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ speed, days }),
    }),
  stopSimulation: () => request('/api/simulation/stop', { method: 'POST' }),
  report: (id, day) => request(`/api/astronauts/${id}/report${q(day)}`, { blob: true }),
}
