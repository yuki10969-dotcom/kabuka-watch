import re

src = open('/mnt/user-data/outputs/kabuka_candle.html', encoding='utf-8').read()

# ===== 1) API URL を /api/stock に変換 =====

# fetchS - 日足
src = src.replace(
    "async function fetchS(code){\n  const t=code+'.T';\n  const px=u=>'https://corsproxy.io/?'+encodeURIComponent(u);\n  const r1=await fetch(px('https://query1.finance.yahoo.com/v8/finance/chart/'+t+'?interval=1d&range=3mo'));\n  const d1=await r1.json();",
    "async function fetchS(code){\n  const r1=await fetch('/api/stock?code='+code+'&interval=1d&range=3mo');\n  const d1=await r1.json();"
)

# fetchS - 週足
src = src.replace(
    "fetch(px('https://query1.finance.yahoo.com/v8/finance/chart/'+t+'?interval=1wk&range=2y'))",
    "fetch('/api/stock?code='+code+'&interval=1wk&range=2y')"
)

# fetchS - PBR summary
src = src.replace(
    "fetch(px('https://query1.finance.yahoo.com/v10/finance/quoteSummary/'+t+'?modules=defaultKeyStatistics'))",
    "fetch('/api/stock?code='+code+'&type=summary')"
)

# loadChart - corsproxy (regex)
src = re.sub(
    r"var url='https://corsproxy\.io/\?'\+encodeURIComponent\([^)]+\);",
    "var url='/api/stock?code='+code+'&interval=1d&range='+r;",
    src
)

remaining = src.count('corsproxy')
print(f'corsproxy remaining: {remaining}')
assert remaining == 0, 'corsproxy still present!'

# ===== 2) <head> に PWA タグを追加 =====
pwa_head = (
    '  <link rel="manifest" href="/manifest.json">\n'
    '  <meta name="theme-color" content="#00e5ff">\n'
    '  <meta name="apple-mobile-web-app-capable" content="yes">\n'
    '  <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">\n'
    '  <meta name="apple-mobile-web-app-title" content="株価Watch">\n'
    '  <link rel="apple-touch-icon" href="/icons/icon-192.png">\n'
)
src = src.replace('<meta charset="UTF-8">', '<meta charset="UTF-8">\n' + pwa_head)

# ===== 3) Service Worker 登録を </body> 直前に追加 =====
sw_script = (
    "\n<script>\n"
    "if('serviceWorker' in navigator){\n"
    "  window.addEventListener('load',function(){\n"
    "    navigator.serviceWorker.register('/sw.js')\n"
    "      .then(function(r){console.log('SW registered',r.scope);})\n"
    "      .catch(function(e){console.log('SW error',e);});\n"
    "  });\n"
    "}\n"
    "</script>\n"
    "</body>"
)
src = src.replace('</body>', sw_script)

# ===== 4) PWAインストールバナーUIを追加 =====
# iOS向け「ホーム画面に追加」プロンプト
pwa_banner_css = """
#pwa-banner{display:none;position:fixed;bottom:0;left:0;right:0;z-index:9999;
  background:linear-gradient(135deg,rgba(6,10,18,.97),rgba(13,21,36,.97));
  border-top:1px solid var(--cyan);padding:16px 20px;
  box-shadow:0 -8px 32px rgba(0,229,255,.15);}
#pwa-banner .pb-row{display:flex;align-items:center;gap:14px;}
#pwa-banner .pb-icon{width:48px;height:48px;border-radius:12px;background:rgba(0,229,255,.1);
  border:1px solid rgba(0,229,255,.3);display:flex;align-items:center;justify-content:center;font-size:24px;flex-shrink:0}
#pwa-banner .pb-text{flex:1}
#pwa-banner .pb-title{font-size:14px;font-weight:900;color:var(--text);margin-bottom:3px}
#pwa-banner .pb-sub{font-size:11px;color:var(--muted)}
#pwa-banner .pb-btns{display:flex;gap:8px;margin-top:12px}
#pwa-banner .pb-install{padding:9px 20px;background:var(--cyan);color:#000;border:none;
  border-radius:8px;font-size:13px;font-weight:900;cursor:pointer;flex:1}
#pwa-banner .pb-close{padding:9px 16px;background:transparent;color:var(--muted);
  border:1px solid var(--border);border-radius:8px;font-size:13px;cursor:pointer}
"""

pwa_banner_html = """
<div id="pwa-banner">
  <div class="pb-row">
    <div class="pb-icon">📈</div>
    <div class="pb-text">
      <div class="pb-title">株価Watch をインストール</div>
      <div class="pb-sub" id="pb-sub">ホーム画面に追加してアプリとして使えます</div>
    </div>
  </div>
  <div class="pb-btns">
    <button class="pb-install" id="pb-install-btn" onclick="pwaInstall()">ホーム画面に追加</button>
    <button class="pb-close" onclick="pwaBannerClose()">後で</button>
  </div>
</div>
"""

pwa_banner_js = """
// ===== PWA Install Banner =====
var _pwaPrompt = null;

window.addEventListener('beforeinstallprompt', function(e) {
  e.preventDefault();
  _pwaPrompt = e;
  // Android: インストールバナー表示
  if (!localStorage.getItem('pwa-dismissed')) {
    document.getElementById('pwa-banner').style.display = 'block';
  }
});

window.addEventListener('appinstalled', function() {
  document.getElementById('pwa-banner').style.display = 'none';
  _pwaPrompt = null;
});

function pwaInstall() {
  if (_pwaPrompt) {
    // Android Chrome: ネイティブプロンプト
    _pwaPrompt.prompt();
    _pwaPrompt.userChoice.then(function(r) {
      _pwaPrompt = null;
      document.getElementById('pwa-banner').style.display = 'none';
    });
  } else {
    // iOS Safari向け案内
    var isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent);
    if (isIOS) {
      alert('iPhoneでインストールするには:\\n\\n① 下の「共有」ボタン（□↑）をタップ\\n② 「ホーム画面に追加」を選択\\n③「追加」をタップ');
    } else {
      alert('ブラウザのメニューから「ホーム画面に追加」または「アプリをインストール」を選択してください');
    }
  }
}

function pwaBannerClose() {
  document.getElementById('pwa-banner').style.display = 'none';
  localStorage.setItem('pwa-dismissed', '1');
}

// iOS: 常にバナー表示（beforeinstallpromptが発火しないため）
(function() {
  var isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
  var isStandalone = window.navigator.standalone;
  if (isIOS && !isStandalone && !localStorage.getItem('pwa-dismissed')) {
    document.getElementById('pb-sub').textContent = '「共有」→「ホーム画面に追加」でインストールできます';
    setTimeout(function() {
      document.getElementById('pwa-banner').style.display = 'block';
    }, 2000);
  }
})();
// ===== PWA END =====
"""

src = src.replace('</style>', pwa_banner_css + '</style>')
src = src.replace('<div class="container">', pwa_banner_html + '<div class="container">')
src = src.replace('render();\n</script>', pwa_banner_js + 'render();\n</script>')

# ===== 5) タイトル変更 =====
src = src.replace('<title>株価アラート</title>', '<title>株価Watch</title>')

print('manifest link:', '/manifest.json' in src)
print('sw register:', 'serviceWorker' in src)
print('pwa banner:', 'pwa-banner' in src)
print('api/stock:', '/api/stock' in src)
print('corsproxy:', src.count('corsproxy'))
print('bytes:', len(src.encode('utf-8')))

open('/home/claude/kabuka-pwa/public/index.html', 'w', encoding='utf-8').write(src)
print('SAVED to public/index.html')
