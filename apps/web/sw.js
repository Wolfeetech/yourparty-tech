// Service Worker for YourParty Radio PWA
const CACHE_NAME = 'yourparty-v7';
const urlsToCache = [
    '/',
    '/wp-content/themes/yourparty-tech/style.css',
    '/wp-content/themes/yourparty-tech/assets/app.js',
    '/wp-content/themes/yourparty-tech/assets/live-voting.js',
    '/wp-content/themes/yourparty-tech/assets/live-voting.css',
    '/wp-content/themes/yourparty-tech/assets/rating-stars.js',
    '/wp-content/themes/yourparty-tech/assets/rating-stars.css'
];

self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => cache.addAll(urlsToCache))
    );
});

self.addEventListener('fetch', event => {
    // Cache-first strategy for static assets, Network-first for everything else
    if (event.request.url.includes('/assets/') || event.request.url.includes('style.css')) {
        event.respondWith(
            caches.match(event.request)
                .then(response => response || fetch(event.request))
        );
    } else {
        event.respondWith(fetch(event.request));
    }
});

self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.filter(name => name !== CACHE_NAME)
                    .map(name => caches.delete(name))
            );
        })
    );
});
