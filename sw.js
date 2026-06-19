// sw.js — ETF PWA Service Worker
const VER   = 'etf-v3';
const SHELL = [
  './', './index.html', './manifest.json',
  './icon-192.png', './icon-512.png',
  './apple-touch-icon.png', './favicon.ico'
];

self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(VER).then(c => c.addAll(SHELL)).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(ks =>
      Promise.all(ks.filter(k => k !== VER).map(k => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);
  if (url.pathname.endsWith('etf_data.json')) {
    // Network first — 數據要新鮮
    e.respondWith(
      fetch(e.request).then(res => {
        caches.open(VER).then(c => c.put(e.request, res.clone()));
        return res;
      }).catch(() => caches.match(e.request))
    );
    return;
  }
  // Cache first — App Shell 離線可用
  e.respondWith(
    caches.match(e.request).then(cached => {
      if (cached) return cached;
      return fetch(e.request).then(res => {
        if (res.ok) caches.open(VER).then(c => c.put(e.request, res.clone()));
        return res;
      });
    })
  );
});
