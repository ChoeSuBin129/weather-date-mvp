const fs = require('fs');
const path = require('path');
const csv = require('csv-parser');

// HTTP URL을 HTTPS로 변환하는 함수
function ensureHttps(url) {
    if (!url) return 'https://via.placeholder.com/300x200';
    if (url.startsWith('https://')) return url;
    if (url.startsWith('http://')) return url.replace('http://', 'https://');
    return url;
}

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
        const events = [];
        const eventsPath = path.join(process.cwd(), 'data', 'events_all.csv');

        // CSV 파일 읽기
        await new Promise((resolve, reject) => {
            fs.createReadStream(eventsPath)
                .pipe(csv())
                .on('data', (data) => events.push(data))
                .on('end', resolve)
                .on('error', reject);
        });

        // 필터 파라미터 가져오기
        const { type, period, location, price } = req.query;
        
        console.log('Filter parameters:', { type, period, location, price });

        // 현재 날짜 계산
        const today = new Date();
        today.setHours(0, 0, 0, 0);

        // 종료 날짜 계산
        let endDate = new Date(today);
        if (period === 'week') {
            endDate.setDate(today.getDate() + 7);
        } else if (period === 'month') {
            endDate.setMonth(today.getMonth() + 1);
        } else if (period === 'all') {
            endDate.setFullYear(today.getFullYear() + 1);
        }

        console.log('Total events before filtering:', events.length);

        // 이벤트 필터링
        let filteredEvents = events.filter(event => {
            const eventStartDate = new Date(event.start_date);
            const eventEndDate = new Date(event.end_date);

            // 기본적으로 종료일이 오늘 이후인 이벤트만 포함
            if (eventEndDate < today) return false;

            // 선택된 기간에 따라 필터링
            if (period === 'today') {
                return eventStartDate <= today && today <= eventEndDate;
            } else {
                return eventStartDate <= endDate;
            }
        });

        console.log('Events after date filtering:', filteredEvents.length);

        // 추가 필터 적용
        if (type && type !== 'all') {
            console.log('Filtering by type:', type);
            const beforeCount = filteredEvents.length;
            filteredEvents = filteredEvents.filter(event => {
                const matches = event.type === type;
                if (matches) console.log('Type match:', event.title, event.type);
                return matches;
            });
            console.log(`Events after type filtering: ${filteredEvents.length} (removed ${beforeCount - filteredEvents.length})`);
        }

        if (location && location !== 'all') {
            console.log('Filtering by location:', location);
            const beforeCount = filteredEvents.length;
            filteredEvents = filteredEvents.filter(event => {
                const matches = event.location === location;
                if (matches) console.log('Location match:', event.title, event.location);
                return matches;
            });
            console.log(`Events after location filtering: ${filteredEvents.length} (removed ${beforeCount - filteredEvents.length})`);
        }

        if (price === 'free') {
            console.log('Filtering for free events');
            const beforeCount = filteredEvents.length;
            filteredEvents = filteredEvents.filter(event => {
                const matches = event.price && (event.price.includes('무료') || event.price.includes('0원'));
                if (matches) console.log('Free price match:', event.title, event.price);
                return matches;
            });
            console.log(`Events after price filtering: ${filteredEvents.length} (removed ${beforeCount - filteredEvents.length})`);
        } else if (price === 'paid') {
            console.log('Filtering for paid events');
            const beforeCount = filteredEvents.length;
            filteredEvents = filteredEvents.filter(event => {
                const matches = event.price && !event.price.includes('무료') && !event.price.includes('0원');
                if (matches) console.log('Paid price match:', event.title, event.price);
                return matches;
            });
            console.log(`Events after price filtering: ${filteredEvents.length} (removed ${beforeCount - filteredEvents.length})`);
        }

        // 이미지 URL을 HTTPS로 변환
        filteredEvents = filteredEvents.map(event => ({
            ...event,
            image: ensureHttps(event.image),
            url: ensureHttps(event.url)
        }));

        // 응답 반환
        res.json({
            success: true,
            events: filteredEvents
        });
    } catch (error) {
        console.error('Error:', error);
        res.status(500).json({
            success: false,
            error: '이벤트 데이터를 가져오는데 실패했습니다.'
        });
    }
};