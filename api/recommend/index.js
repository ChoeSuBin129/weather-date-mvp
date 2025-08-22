const fs = require('fs');
const path = require('path');
const csv = require('csv-parser');

module.exports = async (req, res) => {
    // CORS 설정
    res.setHeader('Access-Control-Allow-Credentials', true);
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS,POST');
    res.setHeader(
        'Access-Control-Allow-Headers',
        'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version'
    );

    // OPTIONS 요청 처리
    if (req.method === 'OPTIONS') {
        res.status(200).end();
        return;
    }

    try {
        // POST 요청이 아닌 경우 에러
        if (req.method !== 'POST') {
            throw new Error('Only POST requests allowed');
        }

        const places = [];
        const placesPath = path.join(process.cwd(), 'data', 'places.csv');

        // CSV 파일 읽기
        await new Promise((resolve, reject) => {
            fs.createReadStream(placesPath)
                .pipe(csv())
                .on('data', (data) => places.push(data))
                .on('end', resolve)
                .on('error', reject);
        });

        // 사용자 설문 데이터
        const {
            district,
            personality,
            drinking,
            active,
            noise,
            romantic,
            budget,
            walk
        } = req.body;

        // 점수 계산 로직
        const recommendations = places.map(place => {
            let score = 0;

            // 지역 가중치 (같은 구는 높은 점수)
            if (place.district === district) {
                score += 0.3;
            }

            // 성격 유형 가중치
            if (personality === 'introvert' && place.noise_level < 0.5) {
                score += 0.2;
            } else if (personality === 'extrovert' && place.noise_level > 0.5) {
                score += 0.2;
            }

            // 음주 여부 가중치
            if (drinking === 'no' && place.alcohol === 'false') {
                score += 0.1;
            } else if (drinking === 'yes' && place.alcohol === 'true') {
                score += 0.1;
            }

            // 활동성 선호도
            score += (1 - Math.abs(active - parseFloat(place.activity_level))) * 0.1;

            // 소음 레벨 선호도
            score += (1 - Math.abs(noise - parseFloat(place.noise_level))) * 0.1;

            // 로맨틱한 분위기 선호도
            score += (1 - Math.abs(romantic - parseFloat(place.romantic_level))) * 0.1;

            // 예산 적합도
            const placeBudget = parseInt(place.budget);
            const userBudget = parseInt(budget);
            if (placeBudget <= userBudget) {
                score += 0.1;
            }

            // 도보 거리 적합도
            const placeDistance = parseFloat(place.distance);
            const userWalk = parseFloat(walk);
            if (placeDistance <= userWalk) {
                score += 0.1;
            }

            return {
                name: place.name,
                type: place.type,
                score: score.toFixed(3),
                reason: score > 0.5 ? '취향 점수 높음' : '기본 추천'
            };
        });

        // 점수순 정렬 및 상위 3개 선택
        const top3 = recommendations
            .sort((a, b) => b.score - a.score)
            .slice(0, 3);

        res.json({
            success: true,
            recommendations: top3
        });
    } catch (error) {
        console.error('Error:', error);
        res.status(500).json({
            success: false,
            error: '추천을 생성하는데 실패했습니다.'
        });
    }
};
