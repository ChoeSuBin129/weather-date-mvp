// Vercel Serverless Function
import { places } from '../data/places.js';

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

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const userPrefs = req.body;

    // 점수 계산
    const scoredPlaces = places.map(place => ({
      ...place,
      score: calculateMatchScore(place, userPrefs)
    }));

    // 상위 5개 장소 선택
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

    return res.status(200).json({
      success: true,
      recommendations,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    console.error('Error:', error);
    return res.status(500).json({
      success: false,
      error: 'Internal server error'
    });
  }
}
