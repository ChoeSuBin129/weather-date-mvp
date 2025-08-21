// Next.js API route support: https://nextjs.org/docs/api-routes/introduction
export default function handler(req, res) {
  // CORS 설정
  res.setHeader('Access-Control-Allow-Credentials', true);
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS,PATCH,DELETE,POST,PUT');
  res.setHeader(
    'Access-Control-Allow-Headers',
    'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version'
  );

  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  if (req.method === 'POST') {
    try {
      const userPrefs = req.body;
      console.log('Received preferences:', userPrefs);

      // 테스트용 응답
      return res.status(200).json({
        success: true,
        recommendations: [
          {
            name: "테스트 장소",
            type: "cafe",
            district: "종로구",
            score: 0.95,
            tags: "테스트",
            indoor: true,
            budget_level: 2
          }
        ],
        timestamp: new Date().toISOString()
      });
    } catch (error) {
      console.error('Error:', error);
      return res.status(500).json({
        success: false,
        error: 'Internal server error',
        details: error.message
      });
    }
  }

  return res.status(405).json({ error: 'Method not allowed' });
}
