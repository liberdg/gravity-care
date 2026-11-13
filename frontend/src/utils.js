// Constantes et fonctions pures (testées dans utils.test.js)

export const INDICATORS = [
  { key: 'heart_rate_rest', label: 'Fréquence cardiaque au repos', unit: 'bpm' },
  { key: 'spo2', label: 'SpO2', unit: '%' },
  { key: 'sleep_hours', label: 'Sommeil', unit: 'h' },
  { key: 'activity_minutes', label: 'Activité physique', unit: 'min' },
  { key: 'hrv', label: 'Variabilité cardiaque (HRV)', unit: 'ms' },
  { key: 'radiation_dose', label: 'Radiations (SIMULÉ, sans portée scientifique)', unit: 'mSv' },
]

export const STATUS_LABELS = {
  vert: 'Normal',
  orange: 'À surveiller',
  rouge: 'Attention requise',
  calibration: 'Calibration',
}

export const ROLE_LABELS = {
  astronaute: 'Astronaute',
  medecin: 'Médecin au sol',
  responsable: 'Responsable de mission',
}

// Fusionne les valeurs journalières et la prévision dans un seul tableau pour le graphique.
// La prévision commence au dernier point réel pour que la ligne en pointillé soit continue.
export function buildChartData(points = [], forecast = []) {
  const data = points.map((p) => ({ day: p.day, value: p.value }))
  if (data.length && forecast.length) {
    data[data.length - 1] = { ...data[data.length - 1], forecast: data[data.length - 1].value }
    for (const f of forecast) data.push({ day: f.day, forecast: f.value })
  }
  return data
}

// Jour de mission le plus récent parmi toutes les séries (ou null).
export function lastDay(daily) {
  const days = Object.values(daily || {}).flatMap((pts) => pts.map((p) => p.day))
  return days.length ? Math.max(...days) : null
}

export function formatDateTime(iso) {
  return iso ? new Date(iso + (iso.endsWith('Z') ? '' : 'Z')).toLocaleString('fr-FR', { timeZone: 'UTC' }) + ' UTC' : '—'
}

// Dernière valeur d'une série et sens de variation par rapport à la veille.
export function latestWithTrend(points = []) {
  if (!points.length) return null
  const last = points[points.length - 1]
  const prev = points.length > 1 ? points[points.length - 2] : null
  const delta = prev ? last.value - prev.value : 0
  return { value: last.value, day: last.day, trend: delta > 0 ? 'up' : delta < 0 ? 'down' : 'flat' }
}

// Analyse de l'adresse (#/dashboard/2 -> { page: 'dashboard', param: 2 })
export function parseRoute(hash) {
  const parts = (hash || '').replace(/^#\/?/, '').split('/').filter(Boolean)
  const page = parts[0] || 'home'
  const param = parts[1] ? Number(parts[1]) : null
  return { page, param: Number.isFinite(param) ? param : null }
}
