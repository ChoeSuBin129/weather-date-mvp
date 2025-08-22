const fs = require('fs');
const path = require('path');
const csv = require('csv-parse/sync');

// CSV 파일에서 장소 데이터 로드
function loadPlacesData() {
  const csvPath = path.join(process.cwd(), 'data', 'places.csv');
  const fileContent = fs.readFileSync(csvPath, 'utf-8');
  return csv.parse(fileContent, {
    columns: true,
    skip_empty_lines: true
  });
}

function calculateMatchScore(place, userPrefs) {
  let score = 0.0;
  const weights = {
    location: 0.2,      // 지역 가중치
    personality: 0.15,  // 성격 유형 가중치
    drinking: 0.1,      // 음주 선호도 가중치
    active: 0.1,        // 활동성 가중치
    noise: 0.15,        // 소음 선호도 가중치
    romantic: 0.15,     // 로맨틱 분위기 가중치
    budget: 0.15        // 예산 가중치
  };

  // 지역 매칭
  if (place.district === userPrefs.district) {
    score += weights.location;
  }

  // 성격 유형 매칭
  if (userPrefs.personality === 'extrovert' && place.extrovert_friendly === 'yes') {
    score += weights.personality;
  } else if (userPrefs.personality === 'introvert' && place.extrovert_friendly === 'no') {
    score += weights.personality;
  }

  // 음주 선호도 매칭
  if (userPrefs.drinking === 'yes' && place.alcohol_available === 'yes') {
    score += weights.drinking;
  } else if (userPrefs.drinking === 'no' && place.alcohol_available === 'no') {
    score += weights.drinking;
  }

  // 활동성/소음 매칭 (noise를 활동성의 proxy로 사용)
  const noiseLevel = parseInt(place.noise) / 5;
  const noiseScore = Math.abs(userPrefs.noise - noiseLevel);
  score += weights.noise * (1 - noiseScore);

  // 로맨틱 분위기 매칭
  const romanticLevel = parseInt(place.romantic) / 5;
  const romanticScore = Math.abs(userPrefs.romantic - romanticLevel);
  score += weights.romantic * (1 - romanticScore);

  // 예산 매칭
  const budgetScore = Math.abs(userPrefs.budget - parseInt(place.budget_level));
  score += weights.budget * (1 - budgetScore / 4);

  return Math.max(0, Math.min(1, score)); // 점수를 0~1 사이로 제한
}

function generateReasonText(place, score) {
  const reasons = [];
  
  if (parseInt(place.romantic) >= 4) {
    reasons.push("로맨틱한 분위기");
  }
  if (place.alcohol_available === 'yes') {
    reasons.push("주류 제공");
  }
  if (parseInt(place.noise) <= 2) {
    reasons.push("조용한 분위기");
  } else if (parseInt(place.noise) >= 4) {
    reasons.push("활기찬 분위기");
  }
  if (parseInt(place.budget_level) <= 2) {
    reasons.push("합리적인 가격");
  }
  if (place.indoor === '1') {
    reasons.push("실내 공간");
  }
  
  // 태그 기반 추가 설명
  const tags = place.tags.split(',');
  if (tags.some(tag => tag.includes('디저트') || tag.includes('베이커리'))) {
    reasons.push("디저트 메뉴");
  }
  if (tags.some(tag => tag.includes('뷰') || tag.includes('전망'))) {
    reasons.push("좋은 전망");
  }

  return reasons.length > 0 ? reasons.join(" / ") : "균형잡힌 선택";
}

module.exports = async (req, res) => {
  // CORS 헤더 설정
  res.setHeader('Access-Control-Allow-Credentials', true);
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS,PATCH,DELETE,POST,PUT');
  res.setHeader(
    'Access-Control-Allow-Headers',
    'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version'
  );

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const userPrefs = req.body;
    console.log('Received preferences:', userPrefs);

    // 장소 데이터 로드
    const places = loadPlacesData();
    console.log(`Loaded ${places.length} places`);

    // 각 장소의 매칭 점수 계산
    const scoredPlaces = places.map(place => {
      const score = calculateMatchScore(place, userPrefs);
      return { ...place, score };
    });

    // 점수순으로 정렬
    scoredPlaces.sort((a, b) => b.score - a.score);

    // 상위 5개 장소 선택
    const recommendations = scoredPlaces.slice(0, 5).map(place => ({
      name: place.name,
      type: place.type,
      district: place.district,
      score: Math.round(place.score * 100) / 100,
      reason: generateReasonText(place, place.score),
      indoor: place.indoor === '1',
      budget_level: parseInt(place.budget_level),
      tags: place.tags
    }));

    return res.status(200).json({
      success: true,
      recommendations
    });
  } catch (error) {
    console.error('Error:', error);
    return res.status(500).json({
      success: false,
      error: 'Internal server error',
      details: error.message
    });
  }
};