// sw.js v4 — 簡化版，不快取 etf_data.json
const VER = 'etf-v4';

self.addEventListener('install', e => {
  self.skipWaiting();
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(ks =>
      Promise.all(ks.map(k => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', e => {
  // 全部 network first，不做快取
  e.respondWith(fetch(e.request).catch(() => caches.match(e.request)));
});
