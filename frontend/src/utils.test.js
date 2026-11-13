import { describe, expect, it } from 'vitest'
import { buildChartData, formatDateTime, INDICATORS, lastDay, ROLE_LABELS, STATUS_LABELS } from './utils.js'

const points = [
  { day: 1, value: 10 },
  { day: 2, value: 11 },
  { day: 3, value: 12 },
]

describe('utils', () => {
  it('construit les données de courbe sans prévision', () => {
    expect(buildChartData(points)).toEqual(points)
  })
  it('relie la prévision au dernier point réel', () => {
    const data = buildChartData(points, [{ day: 4, value: 13 }, { day: 5, value: 14 }])
    expect(data).toHaveLength(5)
    expect(data[2]).toEqual({ day: 3, value: 12, forecast: 12 })
    expect(data[3]).toEqual({ day: 4, forecast: 13 })
  })
  it('gère l\'absence de données', () => {
    expect(buildChartData(undefined, undefined)).toEqual([])
    expect(lastDay({})).toBeNull()
  })
  it('trouve le dernier jour de mission', () => {
    expect(lastDay({ a: points, b: [{ day: 7, value: 1 }] })).toBe(7)
  })
  it('met en forme une date', () => {
    expect(formatDateTime(null)).toBe('—')
    expect(formatDateTime('2026-01-01T08:00:00')).toContain('UTC')
  })
  it('a les 5 indicateurs mesurés et le simulé, sans stress ni humeur', () => {
    const keys = INDICATORS.map((i) => i.key)
    expect(keys).toContain('hrv')
    expect(keys).not.toContain('stress')
    expect(keys).not.toContain('mood')
  })
  it('a un libellé pour chaque statut et rôle', () => {
    for (const s of ['vert', 'orange', 'rouge', 'calibration']) expect(STATUS_LABELS[s]).toBeTruthy()
    for (const r of ['astronaute', 'medecin', 'responsable']) expect(ROLE_LABELS[r]).toBeTruthy()
  })
})
