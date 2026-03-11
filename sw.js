// Service Workerを無効化してキャッシュ問題を解決
self.addEventListener('install', function() {
  self.skipWaiting();
});

self.addEventListener('activate', function(e) {
  e.waitUntil(
    caches.keys().then(function(keys) {
      return Promise.all(keys.map(function(k) { return caches.delete(k); }));
    }).then(function() {
      return self.clients.claim();
    })
  );
});

// キャッシュを使わず常にネットワークから取得
self.addEventListener('fetch', function(e) {
  e.respondWith(fetch(e.request));
});
