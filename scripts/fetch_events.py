import requests
import pandas as pd
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET

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
                    
                    event = {
                        'title': title,
                        'type': self.determine_event_type(title, description),
                        'start_date': start_date,
                        'end_date': end_date,
                        'place': get_text(item, 'eventSite'),
                        'price': get_text(item, 'charge'),
                        'contact': get_text(item, 'contactPoint'),
                        'url': get_text(item, 'url'),
                        'image': get_text(item, 'imageObject'),
                        'description': description.replace('&lt;p&gt;', '').replace('&lt;/p&gt;', '')
                    }
                    
                    # 현재 진행 중인 이벤트만 추가
                    if self.is_ongoing(start_date, end_date):
                        self.events.append(event)
                        print(f"추가됨: {event['title']} ({event['type']})")
                
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