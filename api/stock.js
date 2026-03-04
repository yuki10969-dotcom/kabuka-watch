// Vercel Serverless Function
// Yahoo Finance へのプロキシ - CORSを解決する

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

  const ticker = code.toUpperCase() + '.T';

  try {
    let url;
    if (type === 'summary') {
      url = `https://query1.finance.yahoo.com/v10/finance/quoteSummary/${ticker}?modules=defaultKeyStatistics`;
    } else {
      const iv = interval || '1d';
      const rng = range || '6mo';
      url = `https://query1.finance.yahoo.com/v8/finance/chart/${ticker}?interval=${iv}&range=${rng}`;
    }

    const response = await fetch(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json',
        'Accept-Language': 'ja,en;q=0.9',
      },
    });

    if (!response.ok) {
      return res.status(response.status).json({ error: `Yahoo Finance error: ${response.status}` });
    }

    const data = await response.json();

    // キャッシュ: 5分
    res.setHeader('Cache-Control', 's-maxage=300, stale-while-revalidate=600');
    return res.status(200).json(data);

  } catch (err) {
    console.error('stock API error:', err);
    return res.status(500).json({ error: err.message });
  }
}
