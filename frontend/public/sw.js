// Service worker GRAVITY CARE : interface en cache + dernières données consultées hors-ligne.
// Les réponses de l'API sont gardées dans un cache séparé, vidé à la déconnexion (voir api.js).
const SHELL = 'gravity-care-shell-v1'
const API = 'gravity-care-api-v1'

self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(SHELL).then((c) => c.addAll(['/', '/index.html'])))
  self.skipWaiting()
})

self.addEventListener('activate', (e) => {
  e.waitUntil(self.clients.claim())
})

self.addEventListener('fetch', (e) => {
  const req = e.request
  if (req.method !== 'GET') return
  const url = new URL(req.url)
  if (url.origin !== location.origin) return

  if (url.pathname.startsWith('/api/')) {
    // données : réseau d'abord, cache si hors-ligne
    e.respondWith(
      fetch(req)
        .then((res) => {
          if (res.ok && !url.pathname.includes('/report')) {
            const copy = res.clone()
            caches.open(API).then((c) => c.put(req, copy))
          }
          return res
        })
        .catch(() => caches.match(req).then((hit) => hit || new Response(
          JSON.stringify({ code: 'offline', message: 'Hors-ligne : aucune donnée en cache.' }),
          { status: 503, headers: { 'Content-Type': 'application/json' } },
        ))),
    )
    return
  }
  // interface : cache d'abord, réseau sinon
  e.respondWith(
    caches.match(req).then((hit) => hit || fetch(req).then((res) => {
      if (res.ok) caches.open(SHELL).then((c) => c.put(req, res.clone()))
      return res
    }).catch(() => caches.match('/index.html'))),
  )
})
