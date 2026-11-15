// Punjab Farm Water Watch - Offline & 2G Resilient Service Worker
const CACHE_NAME = 'pww-cache-v2026.11.15.v20';

const CORE_ASSETS = [
    '/',
    '/index.html',
    '/verify.html',
    '/style.css?v=2026.11.15.v20',
    '/app.js?v=2026.11.15.v20',
    '/logo.png',
    '/default_avatar.png',
    '/arnav_sharma.jpg',
    '/chetan_kaushik.jpg',
    '/aryan_sharma.jpg',
    '/amisha_ajana.jpg',
    '/favicon.png',
    '/favicon.ico',
    '/manifest.json',
    '/data/telemetry_en.json',
    '/data/telemetry_hi.json',
    '/data/telemetry_pa.json',
    '/data/telemetry_all.json'
];

// Precache essential assets on install
self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME).then(async cache => {
            console.log('[PWW SW] Pre-caching core offline assets for 2G resiliency...');
            for (const asset of CORE_ASSETS) {
                try {
                    await cache.add(asset);
                } catch (e) {
                    console.warn('[PWW SW] Pre-cache skipped for:', asset, e);
                }
            }
        }).then(() => self.skipWaiting())
    );
});

// Clean up stale caches
self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(keys => {
            return Promise.all(
                keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k))
            );
        }).then(() => self.clients.claim())
    );
});

// Fetch handler: Network-First for HTML/Navigation, Stale-While-Revalidate for Versioned Assets
self.addEventListener('fetch', event => {
    const req = event.request;
    const url = new URL(req.url);

    // Only handle GET requests
    if (req.method !== 'GET') return;

    // 1. Same-origin HTML / Navigation requests: Network-First (Never serve stale HTML when online)
    if (url.origin === self.location.origin) {
        if (req.mode === 'navigate' || req.destination === 'document' || url.pathname === '/' || url.pathname === '/index.html') {
            event.respondWith(
                fetch(req)
                    .then(networkRes => {
                        if (networkRes && networkRes.status === 200) {
                            const copy = networkRes.clone();
                            caches.open(CACHE_NAME).then(cache => cache.put(req, copy));
                        }
                        return networkRes;
                    })
                    .catch(async () => {
                        const cache = await caches.open(CACHE_NAME);
                        return (await cache.match(req)) || (await cache.match('/index.html'));
                    })
            );
            return;
        }

        // Other local assets (CSS, JS, JSON, images): Stale-While-Revalidate
        event.respondWith(
            caches.open(CACHE_NAME).then(async cache => {
                const cached = await cache.match(req);
                const fetchPromise = fetch(req).then(networkRes => {
                    if (networkRes && networkRes.status === 200) {
                        cache.put(req, networkRes.clone());
                    }
                    return networkRes;
                }).catch(() => cached);

                return cached || fetchPromise;
            })
        );
        return;
    }

    // 2. Map tiles and CDN scripts on 2G: Cache-first strategy with timeout fallback
    event.respondWith(
        caches.open(CACHE_NAME).then(async cache => {
            const cached = await cache.match(req);
            if (cached) return cached;

            try {
                const networkRes = await fetch(req);
                if (networkRes && networkRes.status === 200) {
                    cache.put(req, networkRes.clone());
                }
                return networkRes;
            } catch (err) {
                return cached || new Response('', { status: 504, statusText: 'Gateway Timeout on 2G' });
            }
        })
    );
});
