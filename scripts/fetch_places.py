import requests
import pandas as pd
import json
from pathlib import Path
import time

# 네이버 API 설정
NAVER_CLIENT_ID = "9MKoZNP3C4o64zrgNC4a"
NAVER_CLIENT_SECRET = "P9q8GhQF0F"

# 검색할 지역들
DISTRICTS = [
    "서초구", "송파구", "성동구", "용산구", "영등포구",
    "서대문구", "동대문구", "광진구", "강서구"  # 새로운 구들 추가
]

# 검색할 키워드들
KEYWORDS = [
    "카페", "레스토랑", "브런치", "파스타", "와인바",
    "이탈리안", "프렌치", "스페인", "일식", "한식",
    "디저트", "베이커리"
]

def search_places(district, keyword, start=1):
    """네이버 지역검색 API로 장소 검색"""
    url = "https://openapi.naver.com/v1/search/local.json"
    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET
    }
    params = {
        "query": f"{district} {keyword}",
        "display": 10,  # 한 번에 가져올 결과 수 증가 (최대 5개 → 10개)
        "start": start,
        "sort": "random"  # 다양한 결과를 얻기 위해 random 정렬 사용
    }
    
    # API 호출 전 잠시 대기
    time.sleep(1)  # 1초 대기
    
    response = requests.get(url, headers=headers, params=params)
    
    # 429 에러(Too Many Requests) 발생 시 더 오래 대기 후 재시도
    if response.status_code == 429:
        print(f"너무 많은 요청 발생. 10초 대기 후 재시도...")
        time.sleep(10)
        response = requests.get(url, headers=headers, params=params)
    
    response.raise_for_status()
    return response.json()

def get_place_type(title, category):
    """장소 유형 결정"""
    category = category.lower()
    if any(k in category for k in ["카페", "커피", "베이커리", "디저트"]):
        return "cafe"
    return "restaurant"

def extract_place_info(item, district):
    """검색 결과에서 필요한 정보 추출"""
    # 주소에서 위도/경도 추출 (실제로는 geocoding API 사용 필요)
    import random
    lat = 37.5 + random.uniform(-0.1, 0.1)
    lon = 127.0 + random.uniform(-0.1, 0.1)
    
    # 카테고리 기반으로 특성 결정
    category = item["category"].lower()
    noise_level = 3
    romantic_level = 3
    budget_level = 2
    
    # 카테고리 기반 특성 조정
    if "카페" in category or "디저트" in category:
        noise_level = 2
        budget_level = 2
    elif "와인" in category or "프렌치" in category:
        noise_level = 2
        romantic_level = 4
        budget_level = 4
    elif "이탈리안" in category:
        romantic_level = 4
        budget_level = 3
    elif "술집" in category or "포차" in category:
        noise_level = 4
        romantic_level = 2
    
    return {
        "name": item["title"].replace("<b>", "").replace("</b>", ""),
        "type": get_place_type(item["title"], item["category"]),
        "district": district,
        "lat": lat,
        "lon": lon,
        "indoor": 1,
        "noise": noise_level,
        "romantic": romantic_level,
        "budget_level": budget_level,
        "walk_score": 3,
        "alcohol_available": "yes" if any(k in category for k in ["술집", "와인", "포차", "바"]) else "no",
        "extrovert_friendly": "yes" if noise_level >= 3 else "no",
        "tags": item["category"],
        "address": item["address"],
        "phone": item["telephone"]
    }

def main():
    all_places = []
    seen_addresses = set()
    
    for district in DISTRICTS:
        for keyword in KEYWORDS:
            print(f"\n검색중: {district} {keyword}")
            
            try:
                # 첫 페이지 검색
                result = search_places(district, keyword)
                total = min(int(result.get("total", 0)), 30)  # 최대 30개까지만 수집
                
                if "items" in result:
                    for item in result["items"]:
                        if item["address"] in seen_addresses:
                            continue
                            
                        seen_addresses.add(item["address"])
                        place_info = extract_place_info(item, district)
                        all_places.append(place_info)
                        print(f"추가됨: {place_info['name']} ({place_info['type']})")
                
                # 추가 페이지 검색 (최대 3페이지)
                if total > 10:
                    for start in range(11, min(total + 1, 31), 10):
                        print(f"  {start}번째 결과부터 검색 중...")
                        try:
                            more_results = search_places(district, keyword, start)
                            if "items" in more_results:
                                for item in more_results["items"]:
                                    if item["address"] in seen_addresses:
                                        continue
                                    
                                    seen_addresses.add(item["address"])
                                    place_info = extract_place_info(item, district)
                                    all_places.append(place_info)
                                    print(f"추가됨: {place_info['name']} ({place_info['type']})")
                        except Exception as e:
                            print(f"  추가 페이지 검색 중 에러 발생: {e}")
                            time.sleep(5)
                            continue
                
            except Exception as e:
                print(f"에러 발생 ({district} {keyword}): {e}")
                time.sleep(5)  # 에러 발생 시 5초 대기
                continue
    
    if all_places:
        df = pd.DataFrame(all_places)
        df.to_csv("data/new_places.csv", index=False, encoding='utf-8')
        print(f"\n총 {len(df)}개의 장소를 수집했습니다.")
        print("\n수집된 데이터 샘플:")
        print(df[["name", "type", "district", "tags"]].head())
    else:
        print("\n수집된 장소가 없습니다.")

if __name__ == "__main__":
    main()