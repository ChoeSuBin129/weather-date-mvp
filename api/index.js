const places = [
  {
    "place_id": "p001",
    "name": "스타벅스 광화문점",
    "type": "cafe",
    "district": "종로구",
    "indoor": 1,
    "noise": 3,
    "romantic": 2,
    "budget_level": 2,
    "walk_score": 1,
    "alcohol_available": "no",
    "extrovert_friendly": "yes",
    "tags": "프랜차이즈 작업 실내"
  },
  {
    "place_id": "p002",
    "name": "어니언 안국",
    "type": "cafe",
    "district": "종로구",
    "indoor": 1,
    "noise": 2,
    "romantic": 3,
    "budget_level": 3,
    "walk_score": 2,
    "alcohol_available": "no",
    "extrovert_friendly": "no",
    "tags": "베이커리 감성 데이트"
  }
  // ... 나머지 장소 데이터
];

function calculateMatchScore(place, prefs) {
  let score = 0;
  const weights = {
    location: 0.15,
    personality: 0.15,
    drinking: 0.1,
    active: 0.1,
    noise: 0.1,
    romantic: 0.15,
    budget: 0.15,
    walk: 0.1
  };

  // 위치 점수
  if (place.district === prefs.district) {
    score += weights.location;
  }

  // 성격 유형 점수
  if (prefs.personality === 'extrovert' && place.extrovert_friendly === 'yes') {
    score += weights.personality;
  } else if (prefs.personality === 'introvert' && place.extrovert_friendly === 'no') {
    score += weights.personality;
  }

  // 음주 가능 여부
  if (prefs.drinking === 'yes' && place.alcohol_available === 'yes') {
    score += weights.drinking;
  } else if (prefs.drinking === 'no' && place.alcohol_available === 'no') {
    score += weights.drinking;
  }

  // 활동성 점수
  const activityScore = Math.abs(prefs.active - (place.noise / 5));
  score += weights.active * (1 - activityScore);

  // 소음 레벨 선호도
  const noiseScore = Math.abs(prefs.noise - (place.noise / 5));
  score += weights.noise * (1 - noiseScore);

  // 로맨틱한 분위기 선호도
  const romanticScore = Math.abs(prefs.romantic - (place.romantic / 5));
  score += weights.romantic * (1 - romanticScore);

  // 비용 선호도
  const budgetScore = Math.abs(parseInt(prefs.budget) - place.budget_level);
  score += weights.budget * (1 - budgetScore / 4);

  // 도보 거리 선호도
  if (place.walk_score <= parseInt(prefs.walk)) {
    score += weights.walk;
  }

  return score;
}

module.exports = async (req, res) => {
  if (req.method === 'OPTIONS') {
    res.setHeader('Access-Control-Allow-Credentials', true);
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS,PATCH,DELETE,POST,PUT');
    res.setHeader('Access-Control-Allow-Headers', 'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version');
    return res.status(200).end();
  }

  if (req.method === 'POST') {
    try {
      const userPrefs = req.body;
      console.log('Received preferences:', userPrefs);  // 디버깅용 로그

      const scoredPlaces = places.map(place => ({
        ...place,
        score: calculateMatchScore(place, userPrefs)
      }));

      const recommendations = scoredPlaces
        .sort((a, b) => b.score - a.score)
        .slice(0, 5)
        .map(place => ({
          name: place.name,
          type: place.type,
          district: place.district,
          score: Math.round(place.score * 100) / 100,
          tags: place.tags,
          indoor: place.indoor === 1,
          budget_level: parseInt(place.budget_level)
        }));

      console.log('Sending recommendations:', recommendations);  // 디버깅용 로그

      res.setHeader('Access-Control-Allow-Origin', '*');
      return res.status(200).json({
        success: true,
        recommendations,
        timestamp: new Date().toISOString()
      });
    } catch (error) {
      console.error('Error processing request:', error);  // 디버깅용 로그
      return res.status(500).json({
        success: false,
        error: 'Internal server error',
        details: error.message
      });
    }
  }

  return res.status(405).json({ error: 'Method not allowed' });
};
