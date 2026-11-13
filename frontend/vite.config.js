import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// En développement, /api est redirigé vers le backend FastAPI.
// 127.0.0.1 (et non localhost) évite un échec quand « localhost » est résolu en IPv6 (::1).
const BACKEND = 'http://127.0.0.1:8000'

export default defineConfig({
  plugins: [react()],
  server: { port: 5173, proxy: { '/api': BACKEND } },
  preview: { port: 4173, proxy: { '/api': BACKEND } },
  test: { environment: 'node' },
})
