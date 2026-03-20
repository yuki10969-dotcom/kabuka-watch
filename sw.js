const CACHE = 'kbk-v4';
const PRECACHE = ['/manifest.json'];

self.addEventListener('install', function(e) {
  e.waitUntil(
    caches.open(CACHE).then(c => c.addAll(PRECACHE))
  );
  self.skipWaiting();
});

self.addEventListener('activate', function(e) {
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', function(e) {
  // APIリクエスト：常にネットワーク（キャッシュなし）
  if(e.request.url.includes('/api/')) {
    e.respondWith(fetch(e.request).catch(() => new Response('{}', {headers:{'Content-Type':'application/json'}})));
    return;
  }
  // HTMLナビゲーション（/ や index.html）：常にネットワーク最新を取得
  // キャッシュには保存せず、オフライン時のみキャッシュにフォールバック
  if(e.request.mode === 'navigate') {
    e.respondWith(
      fetch(e.request)
        .catch(() => caches.match('/index.html'))
    );
    return;
  }
  // その他の静的アセット：ネットワーク優先、失敗時はキャッシュ
  e.respondWith(
    fetch(e.request)
      .then(res => {
        const clone = res.clone();
        caches.open(CACHE).then(c => c.put(e.request, clone));
        return res;
      })
      .catch(() => caches.match(e.request))
  );
});
