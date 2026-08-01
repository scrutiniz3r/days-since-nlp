// Minimal service worker — required by Chrome/Android for the automatic
// "Install app" prompt to fire. Also gives basic offline capability by
// caching the app shell.
const CACHE_NAME = 'days-since-v3';
const APP_SHELL = [
  './',
  './index.html',
  './manifest.json',
  './icon-192.png',
  './icon-512.png',
  './badge-192.png'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(APP_SHELL))
  );
  self.skipWaiting();
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(names =>
      Promise.all(names.filter(n => n !== CACHE_NAME).map(n => caches.delete(n)))
    )
  );
  self.clients.claim();
});

// Network-first for everything — this app is data-driven (Firebase, HF API)
// so we always want fresh content when online, falling back to cache only
// when offline.
self.addEventListener('fetch', event => {
  if (event.request.method !== 'GET') return;
  event.respondWith(
    fetch(event.request)
      .then(res => {
        const resClone = res.clone();
        caches.open(CACHE_NAME).then(cache => cache.put(event.request, resClone));
        return res;
      })
      .catch(() => caches.match(event.request))
  );
});

// Tapping a notification does nothing by default — this is what actually
// opens (or focuses, if already open) the app when you tap on one.
self.addEventListener('notificationclick', event => {
  event.notification.close();
  event.waitUntil(
    self.clients.matchAll({ type: 'window', includeUncontrolled: true }).then(clientList => {
      for (const client of clientList) {
        // Already open in a tab — just bring it to the front
        if ('focus' in client) return client.focus();
      }
      // Not open anywhere — open a new window/tab
      if (self.clients.openWindow) return self.clients.openWindow('./index.html');
    })
  );
});
