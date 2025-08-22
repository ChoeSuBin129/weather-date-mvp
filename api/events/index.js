const fs = require('fs');
const path = require('path');
const csv = require('csv-parser');

module.exports = async (req, res) => {
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

        // 추가 필터 적용
        if (type && type !== 'all') {
            filteredEvents = filteredEvents.filter(event => event.type === type);
        }
        if (location && location !== 'all') {
            filteredEvents = filteredEvents.filter(event => 
                event.place && event.place.includes(location)
            );
        }
        if (price === 'free') {
            filteredEvents = filteredEvents.filter(event => 
                event.price && (event.price.includes('무료') || event.price.includes('0원'))
            );
        } else if (price === 'paid') {
            filteredEvents = filteredEvents.filter(event => 
                event.price && !event.price.includes('무료') && !event.price.includes('0원')
            );
        }

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
