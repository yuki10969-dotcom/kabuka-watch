// Vercel Serverless Function
// Yahoo Finance へのプロキシ - CORSを解決する

const YF_HEADERS = {
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
  'Accept': 'application/json',
  'Accept-Language': 'ja,en;q=0.9',
};

async function fetchYahoo(url) {
  const res = await fetch(url, { headers: YF_HEADERS });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

export default async function handler(req, res) {
  // CORS ヘッダー
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  const { code, interval, range, type } = req.query;

  if (!code) {
    return res.status(400).json({ error: 'code is required' });
  }

  // 指数・為替は.Tを付けない（^N225, ^TPX, USDJPY=Xなど）
  const isSpecial = code.startsWith('^') || code.includes('=') || code.includes('.');
  const ticker = isSpecial ? code : code.toUpperCase() + '.T';

  const iv = interval || '1d';
  const rng = range || '6mo';

  try {
    let data;

    // 998405.T（TOPIX）は Yahoo Finance Japan を優先して試みる
    if (ticker === '998405.T' && type !== 'summary') {
      const jpUrl = `https://query1.finance.yahoo.co.jp/v8/finance/chart/998405.T?interval=${iv}&range=${rng}&lang=ja&region=JP`;
      try {
        data = await fetchYahoo(jpUrl);
        // price データが入っているか確認
        const price = data?.chart?.result?.[0]?.meta?.regularMarketPrice;
        if (!price) throw new Error('no price in JP response');
      } catch (jpErr) {
        // JP API失敗時は US API で 1306.T（TOPIX連動ETF）にフォールバック
        console.warn('Yahoo Finance JP failed, falling back to 1306.T:', jpErr.message);
        const usUrl = `https://query1.finance.yahoo.com/v8/finance/chart/1306.T?interval=${iv}&range=${rng}`;
        data = await fetchYahoo(usUrl);
      }
    } else {
      let url;
      if (type === 'summary') {
        url = `https://query1.finance.yahoo.com/v10/finance/quoteSummary/${ticker}?modules=defaultKeyStatistics`;
      } else {
        url = `https://query1.finance.yahoo.com/v8/finance/chart/${ticker}?interval=${iv}&range=${rng}`;
      }
      data = await fetchYahoo(url);
    }

    // キャッシュ: 5分
    res.setHeader('Cache-Control', 's-maxage=300, stale-while-revalidate=600');
    return res.status(200).json(data);

  } catch (err) {
    console.error('stock API error:', err);
    return res.status(500).json({ error: err.message });
  }
}
