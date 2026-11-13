// Illustrations et icônes dessinées en SVG : aucune image externe, tout marche hors-ligne.

const ICONS = {
  heart: 'M12 21s-7-4.5-9.5-9A5.5 5.5 0 0 1 12 6a5.5 5.5 0 0 1 9.5 6c-2.5 4.5-9.5 9-9.5 9z',
  drop: 'M12 3s6 6.5 6 11a6 6 0 0 1-12 0c0-4.5 6-11 6-11z',
  moon: 'M20 14.5A8 8 0 1 1 9.5 4a6.5 6.5 0 0 0 10.5 10.5z',
  bolt: 'M13 2L4 14h7l-1 8 9-12h-7l1-8z',
  wave: 'M2 12h4l2-6 4 12 3-9 2 3h5',
  sun: 'M12 3v3M12 18v3M3 12h3M18 12h3M5.6 5.6l2.1 2.1M16.3 16.3l2.1 2.1M18.4 5.6l-2.1 2.1M7.7 16.3l-2.1 2.1M12 8.5a3.5 3.5 0 1 0 0 7a3.5 3.5 0 0 0 0-7z',
  sensor: 'M4.9 19.1a10 10 0 0 1 0-14.2M19.1 4.9a10 10 0 0 1 0 14.2M8.1 15.9a5.5 5.5 0 0 1 0-7.8M15.9 8.1a5.5 5.5 0 0 1 0 7.8M12 10.5a1.5 1.5 0 1 0 0 3a1.5 1.5 0 0 0 0-3z',
  chart: 'M3 20h18M6 16v-5M11 16V6M16 16v-8',
  bell: 'M6 16v-5a6 6 0 0 1 12 0v5l2 2H4zM10 20a2 2 0 0 0 4 0',
  shield: 'M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z',
  check: 'M5 12.5l4.5 4.5L19 7.5',
  search: 'M11 4a7 7 0 1 0 0 14a7 7 0 0 0 0-14zM21 21l-5-5',
  offline: 'M3 3l18 18M5 12.5a10 10 0 0 1 3-2M2 9a15 15 0 0 1 4-2.5M12 20h.01M9 16.5a5 5 0 0 1 3-1M17 12.5a10 10 0 0 0-3-2M22 9a15 15 0 0 0-9-4',
  user: 'M12 12a4 4 0 1 0 0-8a4 4 0 0 0 0 8zM4 21a8 8 0 0 1 16 0',
  play: 'M7 4l13 8-13 8z',
  stop: 'M6 6h12v12H6z',
}

export function Icon({ name, size = 22, color = 'currentColor' }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="1.8"
         strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d={ICONS[name]} />
    </svg>
  )
}

export const INDICATOR_ICON = {
  heart_rate_rest: 'heart', spo2: 'drop', sleep_hours: 'moon', activity_minutes: 'bolt', hrv: 'wave', radiation_dose: 'sun',
}

export function Logo({ size = 30 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 40 40" aria-hidden="true">
      <defs>
        <linearGradient id="lg" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor="#38bdf8" /><stop offset="1" stopColor="#8b5cf6" />
        </linearGradient>
      </defs>
      <circle cx="20" cy="20" r="9" fill="url(#lg)" />
      <ellipse cx="20" cy="20" rx="18" ry="7" fill="none" stroke="#7dd3fc" strokeWidth="1.6" transform="rotate(-25 20 20)" />
      <circle cx="35" cy="11" r="2.4" fill="#fbbf24" />
    </svg>
  )
}

// Étoiles à positions fixes (même rendu à chaque affichage)
const STARS = (() => {
  let s = 7
  const rnd = () => ((s = (s * 9301 + 49297) % 233280) / 233280)
  return Array.from({ length: 70 }, () => ({ x: rnd() * 520, y: rnd() * 420, r: 0.5 + rnd() * 1.4, o: 0.3 + rnd() * 0.7 }))
})()

export function HeroArt() {
  return (
    <svg viewBox="0 0 520 420" className="hero-art" role="img" aria-label="Terre, orbite et signal cardiaque">
      <defs>
        <radialGradient id="earth" cx="35%" cy="32%" r="75%">
          <stop offset="0" stopColor="#67e8f9" /><stop offset="0.45" stopColor="#2563eb" /><stop offset="1" stopColor="#0b1d4d" />
        </radialGradient>
        <radialGradient id="glow" cx="50%" cy="50%" r="50%">
          <stop offset="0.6" stopColor="#38bdf8" stopOpacity="0.35" /><stop offset="1" stopColor="#38bdf8" stopOpacity="0" />
        </radialGradient>
        <clipPath id="clipEarth"><circle cx="260" cy="215" r="115" /></clipPath>
      </defs>
      {STARS.map((s, i) => <circle key={i} cx={s.x} cy={s.y} r={s.r} fill="#fff" opacity={s.o} />)}
      <circle cx="450" cy="70" r="22" fill="#cbd5e1" opacity="0.9" />
      <circle cx="441" cy="63" r="5" fill="#94a3b8" opacity="0.7" /><circle cx="458" cy="78" r="3.5" fill="#94a3b8" opacity="0.7" />
      <circle cx="260" cy="215" r="150" fill="url(#glow)" />
      <circle cx="260" cy="215" r="115" fill="url(#earth)" />
      <g clipPath="url(#clipEarth)" fill="#34d399" opacity="0.55">
        <ellipse cx="215" cy="185" rx="42" ry="26" transform="rotate(-20 215 185)" />
        <ellipse cx="300" cy="250" rx="38" ry="22" transform="rotate(25 300 250)" />
        <ellipse cx="240" cy="290" rx="30" ry="14" />
      </g>
      <ellipse cx="260" cy="215" rx="205" ry="62" fill="none" stroke="#7dd3fc" strokeWidth="1.5" strokeDasharray="5 6" transform="rotate(-18 260 215)" />
      <g transform="translate(437 165) rotate(-18)">
        <rect x="-9" y="-5" width="18" height="10" rx="2" fill="#e2e8f0" />
        <rect x="-26" y="-3" width="14" height="6" fill="#38bdf8" /><rect x="12" y="-3" width="14" height="6" fill="#38bdf8" />
      </g>
      <path d="M40 360 H170 L190 328 L214 392 L240 306 L266 368 L288 356 L306 360 H480" fill="none" stroke="#22d3ee"
            strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" className="ecg" />
    </svg>
  )
}

const RING = { vert: '#2e9e6b', orange: '#e08a1e', rouge: '#d64545', calibration: '#64748b' }

export function AstronautAvatar({ code, status = 'calibration', size = 64 }) {
  const ring = RING[status] || RING.calibration
  const id = `v${code}`
  return (
    <svg width={size} height={size} viewBox="0 0 80 80" aria-hidden="true">
      <defs>
        <linearGradient id={id} x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor="#1e3a8a" /><stop offset="1" stopColor="#0f172a" />
        </linearGradient>
      </defs>
      <circle cx="40" cy="40" r="37" fill="#0f172a" stroke={ring} strokeWidth="3" />
      <path d="M14 70a26 22 0 0 1 52 0z" fill="#e2e8f0" />
      <circle cx="40" cy="36" r="21" fill="#f1f5f9" />
      <ellipse cx="40" cy="37" rx="15" ry="12.5" fill={`url(#${id})`} />
      <ellipse cx="34" cy="32" rx="5" ry="3" fill="#7dd3fc" opacity="0.55" />
      <circle cx="40" cy="70" r="7" fill={ring} />
      <text x="40" y="73.5" textAnchor="middle" fontSize="9" fontWeight="700" fill="#fff">{code}</text>
    </svg>
  )
}
