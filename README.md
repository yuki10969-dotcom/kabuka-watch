# 株価Watch - PWA デプロイ手順

スマホでも使えるPWA（Progressive Web App）です。
URLを開くだけ、またはホーム画面に追加してアプリとして使えます。

---

## 📁 ファイル構成

```
kabuka-pwa/
├── api/
│   └── stock.js          ← Yahoo Finance プロキシ（Vercel Serverless）
├── public/
│   ├── index.html        ← メインアプリ
│   ├── manifest.json     ← PWA設定
│   ├── sw.js             ← Service Worker（オフラインキャッシュ）
│   └── icons/
│       ├── icon-192.png
│       └── icon-512.png
├── vercel.json           ← Vercel設定
├── package.json
└── README.md
```

---

## 🚀 デプロイ手順（30分で完了）

### ステップ1: GitHubにアップロード

1. [github.com](https://github.com) でアカウント作成（すでにある場合はスキップ）
2. 右上「+」→「New repository」
3. Repository name: `kabuka-watch`
4. 「Create repository」をクリック
5. 「uploading an existing file」をクリック
6. このフォルダ内の**全ファイルをドラッグ＆ドロップ**
   - `api/stock.js`
   - `public/index.html`
   - `public/manifest.json`
   - `public/sw.js`
   - `public/icons/icon-192.png`
   - `public/icons/icon-512.png`
   - `vercel.json`
   - `package.json`
7. 「Commit changes」をクリック

> ⚠️ フォルダ構造を維持してアップロードしてください（api/ と public/ のフォルダごと）

### ステップ2: Vercelにデプロイ

1. [vercel.com](https://vercel.com) にアクセス
2. 「Sign Up」→「Continue with GitHub」でGitHubアカウントでログイン
3. 「Add New Project」→「Import Git Repository」
4. `kabuka-watch` を選択して「Import」
5. 設定はそのまま「Deploy」をクリック
6. 2〜3分でデプロイ完了！

### ステップ3: URLを確認

デプロイ完了後、以下のようなURLが発行されます：
```
https://kabuka-watch.vercel.app
```

---

## 📱 スマホへのインストール方法

### iPhoneの場合
1. Safari でアプリのURLを開く
2. 下の「共有」ボタン（□↑）をタップ
3. 「ホーム画面に追加」をタップ
4. 「追加」をタップ → 完了！

### Androidの場合
1. Chrome でアプリのURLを開く
2. 自動的にインストールバナーが表示される
3. 「ホーム画面に追加」をタップ → 完了！

または：ブラウザメニュー（⋮）→「アプリをインストール」

---

## 🔧 更新方法

HTMLやJSを修正したい場合：
1. GitHubのリポジトリで該当ファイルを編集
2. 「Commit changes」→ Vercelが自動で再デプロイ

---

## ⚠️ 注意事項

- **Yahoo Finance APIの制限**: 無料で使えますが、大量アクセス時に制限される場合があります
- **データ保存**: トレード記録・銘柄リストは各自のブラウザ（LocalStorage）に保存されます。デバイスをまたいで同期したい場合はログイン機能の追加が必要です
- **Vercel無料プランの制限**: 月100GBの転送量、サーバーレス関数は月100時間まで（一般的な利用では十分）

---

## 💡 将来の拡張案

- Firebase/Supabase でユーザーログイン＆クラウド同期
- Push通知でアラートをスマホに送信
- Apple Watch対応
