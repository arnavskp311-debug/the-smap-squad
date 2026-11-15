// Punjab Farm Water Watch - Offline & 2G Resilient Service Worker
const CACHE_NAME = 'pww-cache-v2026.11.15.v11';

const CORE_ASSETS = [
    '/',
    '/index.html',
    '/verify.html',
    '/style.css?v=2026.11.15.v11',
    '/app.js?v=2026.11.15.v11',
    '/logo.png',
    '/default_avatar.png',
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

// Fetch with Stale-While-Revalidate for local files & Cache-First for maps/CDNs
self.addEventListener('fetch', event => {
    const req = event.request;
    const url = new URL(req.url);

    // Only handle GET requests
    if (req.method !== 'GET') return;

    // 1. Same-origin assets (HTML, CSS, JS, JSON telemetry): Stale-While-Revalidate
    if (url.origin === self.location.origin) {
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
