const CACHE_NAME = 'bibleweb-cache-v2';

const PRECACHE_ASSETS = [
    '/',
    '/read',
    '/plans',
    '/bookmarks',
    '/presenter',
    '/static/manifest.json',
    '/static/icons/icon-192.png',
    '/static/js/storage.js',
    '/static/js/audio_player.js',
    '/static/plans/plan_100_new_testament.json',
    '/static/plans/plan_100_whole_bible.json'
];

self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            return cache.addAll(PRECACHE_ASSETS);
        }).then(() => self.skipWaiting())
    );
});

self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((keys) => {
            return Promise.all(
                keys.map((key) => {
                    if (key !== CACHE_NAME) {
                        return caches.delete(key);
                    }
                })
            );
        }).then(() => self.clients.claim())
    );
});

self.addEventListener('fetch', (event) => {
    const request = event.request;
    const url = new URL(request.url);

    // Dynamic cache for static assets & plans API
    if (url.pathname.startsWith('/static/') || url.pathname.startsWith('/api/plans')) {
        event.respondWith(
            caches.open(CACHE_NAME).then((cache) => {
                return cache.match(request).then((cachedResponse) => {
                    const fetchPromise = fetch(request).then((networkResponse) => {
                        if (networkResponse && networkResponse.status === 200) {
                            cache.put(request, networkResponse.clone());
                        }
                        return networkResponse;
                    }).catch(() => cachedResponse);

                    return cachedResponse || fetchPromise;
                });
            })
        );
        return;
    }

    // HTML Navigation requests - Network first with precache fallback
    if (request.mode === 'navigate') {
        event.respondWith(
            fetch(request).catch(async () => {
                const cache = await caches.open(CACHE_NAME);
                const matched = await cache.match(request);
                return matched || cache.match('/read') || cache.match('/');
            })
        );
        return;
    }

    // Default Cache First
    event.respondWith(
        caches.match(request).then((response) => response || fetch(request))
    );
});