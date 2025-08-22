import requests
import pandas as pd
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
import re

class KcisaEventFetcher:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.kcisa.kr/openapi/CNV_060/request"
        self.events = []

    def determine_event_type(self, title, description):
        """제목과 설명을 기반으로 이벤트 타입을 결정"""
        title_lower = title.lower() if title else ""
        desc_lower = description.lower() if description else ""
        
        # 전시 관련 키워드
        exhibition_keywords = ['전시', '展', '작품전', '기획전', '특별전', '아트', '미술', '갤러리']
        
        # 공연 관련 키워드
        performance_keywords = ['공연', '연극', '뮤지컬', '콘서트', '오페라', '연주회', '페스티벌']
        
        # 축제 관련 키워드
        festival_keywords = ['축제', '페스타', '페어', '마켓']
        
        # 전시 체크
        for keyword in exhibition_keywords:
            if keyword in title_lower or keyword in desc_lower:
                return '전시'
        
        # 공연 체크
        for keyword in performance_keywords:
            if keyword in title_lower or keyword in desc_lower:
                return '공연'
        
        # 축제 체크
        for keyword in festival_keywords:
            if keyword in title_lower or keyword in desc_lower:
                return '축제'
        
        return '기타'  # 기본값

    def determine_location(self, title, place, contact, description):
        """제목, 장소, 연락처, 설명을 기반으로 지역을 결정"""
        # 모든 텍스트를 하나로 합침
        all_text = ' '.join(filter(None, [
            title or '',
            place or '',
            contact or '',
            description or ''
        ])).lower()

        # 지역 정보 추출
        # 1. [지역명] 패턴 체크
        location_match = re.search(r'\[(.*?)\]', title or '')
        if location_match:
            location = location_match.group(1)
            # 광역시/도 이름만 추출
            for region in ['서울', '부산', '대구', '인천', '광주', '대전', '울산', '세종',
                         '경기', '강원', '충북', '충남', '전북', '전남', '경북', '경남', '제주']:
                if region in location:
                    return region

        # 2. 지역명이 포함된 경우
        regions = {
            '서울': ['서울', '강남', '강북', '강서', '강동', '마포', '서초', '송파', '종로', '중구', '용산'],
            '부산': ['부산', '해운대', '부산진', '동래', '남구', '북구', '사상', '사하'],
            '대구': ['대구', '수성', '달서', '달성'],
            '인천': ['인천', '부평', '계양', '남동', '서구', '연수'],
            '광주': ['광주', '광산', '남구', '북구', '서구'],
            '대전': ['대전', '대덕', '유성', '서구', '중구'],
            '울산': ['울산', '남구', '동구', '북구', '울주'],
            '세종': ['세종'],
            '경기': ['경기', '수원', '성남', '고양', '용인', '부천', '안산', '남양주', '안양', '평택', '시흥', '파주', '의정부', '김포', '광주', '광명', '군포', '오산', '이천', '양주', '구리', '안성', '포천', '의왕', '하남', '여주', '양평', '동두천', '과천', '가평', '연천'],
            '강원': ['강원', '춘천', '원주', '강릉', '동해', '태백', '속초', '삼척', '홍천', '횡성', '영월', '평창', '정선', '철원', '화천', '양구', '인제', '고성', '양양'],
            '충북': ['충북', '청주', '충주', '제천', '보은', '옥천', '영동', '증평', '진천', '괴산', '음성', '단양'],
            '충남': ['충남', '천안', '공주', '보령', '아산', '서산', '논산', '계룡', '당진', '금산', '부여', '서천', '청양', '홍성', '예산', '태안'],
            '전북': ['전북', '전주', '군산', '익산', '정읍', '남원', '김제', '완주', '진안', '무주', '장수', '임실', '순창', '고창', '부안'],
            '전남': ['전남', '목포', '여수', '순천', '나주', '광양', '담양', '곡성', '구례', '고흥', '보성', '화순', '장흥', '강진', '해남', '영암', '무안', '함평', '영광', '장성', '완도', '진도', '신안'],
            '경북': ['경북', '포항', '경주', '김천', '안동', '구미', '영주', '영천', '상주', '문경', '경산', '군위', '의성', '청송', '영양', '영덕', '청도', '고령', '성주', '칠곡', '예천', '봉화', '울진', '울릉'],
            '경남': ['경남', '창원', '진주', '통영', '사천', '김해', '밀양', '거제', '양산', '의령', '함안', '창녕', '고성', '남해', '하동', '산청', '함양', '거창', '합천'],
            '제주': ['제주', '서귀포']
        }

        for region, keywords in regions.items():
            for keyword in keywords:
                if keyword in all_text:
                    return region

        # 3. 전화번호 지역번호로 체크
        area_codes = {
            '02': '서울',
            '051': '부산',
            '053': '대구',
            '032': '인천',
            '062': '광주',
            '042': '대전',
            '052': '울산',
            '044': '세종',
            '031': '경기',
            '033': '강원',
            '043': '충북',
            '041': '충남',
            '063': '전북',
            '061': '전남',
            '054': '경북',
            '055': '경남',
            '064': '제주'
        }
        
        phone_match = re.search(r'(\d{2,3})-?\d{3,4}-?\d{4}', all_text)
        if phone_match:
            area_code = phone_match.group(1)
            if area_code in area_codes:
                return area_codes[area_code]

        return None  # 지역을 특정할 수 없는 경우

    def determine_price(self, title, description, charge):
        """제목, 설명, 요금 정보를 기반으로 가격을 결정"""
        # 모든 텍스트를 하나로 합침
        all_text = ' '.join(filter(None, [
            title or '',
            description or '',
            charge or ''
        ])).lower()

        # 무료 키워드 체크
        free_keywords = ['무료', '무료관람', '무료입장', '무료입니다', '무료로', '0원']
        for keyword in free_keywords:
            if keyword in all_text:
                return '무료'

        # 유료 키워드 체크
        paid_keywords = ['유료', '원', '만원', '천원', '유료입장', '입장료', '관람료', '예매']
        for keyword in paid_keywords:
            if keyword in all_text:
                # 가격이 명시되어 있는 경우
                price_match = re.search(r'(\d+[,\d]*)[원만천]', all_text)
                if price_match:
                    return f"{price_match.group(1)}원"
                return '유료'  # 구체적인 가격이 없는 경우

        return '가격 정보 없음'  # 가격 정보를 찾을 수 없는 경우

    def fetch_events(self):
        """공연/전시 정보 가져오기"""
        try:
            # 페이지별로 데이터 가져오기 (최대 100개)
            for page in range(1, 11):  # 10페이지까지
                params = {
                    'serviceKey': self.api_key,
                    'numOfRows': '100',
                    'pageNo': str(page),
                    'dataType': 'xml'
                }
                
                print(f"\n=== {page}페이지 데이터 수집 중... ===")
                print(f"요청 URL: {self.base_url}")
                print(f"파라미터: {params}")
                
                response = requests.get(self.base_url, params=params)
                print(f"응답 상태: {response.status_code}")
                print(f"응답 내용 일부: {response.text[:500]}...")
                
                response.raise_for_status()
                
                # XML 파싱
                root = ET.fromstring(response.text)
                items = root.findall('.//item')
                
                if not items:
                    print("더 이상 데이터가 없습니다.")
                    break
                    
                for item in items:
                    # XML 요소에서 텍스트 추출
                    def get_text(item, tag):
                        element = item.find(tag)
                        return element.text if element is not None else ''
                    
                    # 날짜 형식 변환 (period: "YYYYMMDD ~ YYYYMMDD")
                    period = get_text(item, 'period')
                    if period and ' ~ ' in period:
                        start_date, end_date = period.split(' ~ ')
                        start_date = f"{start_date[:4]}-{start_date[4:6]}-{start_date[6:]}"
                        end_date = f"{end_date[:4]}-{end_date[4:6]}-{end_date[6:]}"
                    else:
                        start_date = end_date = None
                    
                    title = get_text(item, 'title')
                    description = get_text(item, 'description')
                    place = get_text(item, 'eventSite')
                    contact = get_text(item, 'contactPoint')
                    charge = get_text(item, 'charge')
                    
                    event = {
                        'title': title,
                        'type': self.determine_event_type(title, description),
                        'start_date': start_date,
                        'end_date': end_date,
                        'place': place,
                        'location': self.determine_location(title, place, contact, description),
                        'price': self.determine_price(title, description, charge),
                        'contact': contact,
                        'url': get_text(item, 'url'),
                        'image': get_text(item, 'imageObject'),
                        'description': description.replace('&lt;p&gt;', '').replace('&lt;/p&gt;', '')
                    }
                    
                    # 현재 진행 중인 이벤트만 추가
                    if self.is_ongoing(start_date, end_date):
                        self.events.append(event)
                        print(f"추가됨: {event['title']} ({event['type']}) - {event['location'] or '지역 미상'} - {event['price']}")
                
                print(f"현재까지 {len(self.events)}개의 이벤트가 수집되었습니다.")
                
        except Exception as e:
            print(f"API 에러: {e}")

    def is_ongoing(self, start_date, end_date):
        """현재 진행 중인 이벤트인지 확인"""
        try:
            today = datetime.now().date()
            start = datetime.strptime(start_date, '%Y-%m-%d').date() if start_date else None
            end = datetime.strptime(end_date, '%Y-%m-%d').date() if end_date else None
            
            if not start or not end:
                return False
                
            return start <= today <= end
        except:
            return False

    def save_events(self):
        """수집한 이벤트를 CSV 파일로 저장"""
        if not self.events:
            print("저장할 이벤트가 없습니다.")
            return
            
        df = pd.DataFrame(self.events)
        
        # 전체 데이터 저장
        df.to_csv("data/events_all.csv", index=False, encoding='utf-8')
        print(f"\n전체 {len(df)}개의 이벤트를 data/events_all.csv에 저장했습니다.")

def main():
    # API 키 설정
    API_KEY = "dafb665b-5e08-4841-901d-22313f8a4931"
    
    # 이벤트 수집기 생성
    fetcher = KcisaEventFetcher(API_KEY)
    
    # 공연/전시 정보 가져오기
    print("\n=== 공연/전시 정보 수집 중... ===")
    fetcher.fetch_events()
    
    # 이벤트 저장
    print("\n=== 수집한 이벤트 저장 중... ===")
    fetcher.save_events()

if __name__ == "__main__":
    main()