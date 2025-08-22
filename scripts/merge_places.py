import pandas as pd
import numpy as np
import re

def load_csv(file_path):
    """CSV 파일 로드"""
    try:
        return pd.read_csv(file_path)
    except Exception as e:
        print(f"파일 로드 중 에러 발생 ({file_path}): {e}")
        return None

def clean_place_name(name):
    """장소 이름 정리 (HTML 태그 제거, 공백 정리)"""
    return name.replace("<b>", "").replace("</b>", "").strip()

def get_next_place_id(existing_ids):
    """다음 place_id 생성"""
    if not existing_ids:
        return "p001"
    
    # 기존 ID에서 숫자만 추출하여 최대값 찾기
    id_numbers = [int(re.search(r'p(\d+)', str(id_)).group(1)) 
                 for id_ in existing_ids if pd.notna(id_)]
    max_id = max(id_numbers) if id_numbers else 0
    return f"p{str(max_id + 1).zfill(3)}"

def merge_places():
    """기존 데이터와 새로운 데이터 병합"""
    # 파일 로드
    existing_df = load_csv("data/places.csv")
    new_df = load_csv("data/new_places.csv")
    
    if existing_df is None or new_df is None:
        print("데이터 로드 실패")
        return
    
    print(f"기존 데이터: {len(existing_df)}개 장소")
    print(f"새로운 데이터: {len(new_df)}개 장소")
    
    # 새로운 데이터 전처리
    new_df['name'] = new_df['name'].apply(clean_place_name)
    
    # 필요한 컬럼만 선택하고 없는 컬럼은 기본값으로 설정
    required_columns = {
        'place_id': None,
        'name': None,
        'type': None,
        'district': None,
        'lat': None,
        'lon': None,
        'indoor': 1,  # 대부분 실내라고 가정
        'noise': 3,   # 중간 값으로 설정
        'romantic': 3,
        'budget_level': 2,
        'walk_score': 3,
        'alcohol_available': 'no',
        'extrovert_friendly': 'yes',
        'tags': ''
    }
    
    # 새로운 데이터에 없는 컬럼 추가
    for col, default_value in required_columns.items():
        if col not in new_df.columns:
            new_df[col] = default_value
    
    # 기존 데이터와 새로운 데이터 병합
    merged_df = pd.concat([
        existing_df[required_columns.keys()],
        new_df[required_columns.keys()]
    ], ignore_index=True)
    
    # 중복 제거 (장소 이름과 district가 같으면 중복으로 간주)
    merged_df = merged_df.drop_duplicates(subset=['name', 'district'], keep='first')
    
    # place_id가 없는 행에 새로운 ID 부여
    existing_ids = existing_df['place_id'].tolist()
    next_id = get_next_place_id(existing_ids)
    
    for idx in merged_df.index:
        if pd.isna(merged_df.loc[idx, 'place_id']):
            merged_df.loc[idx, 'place_id'] = next_id
            next_id = get_next_place_id([next_id])
    
    # 결과 저장
    output_path = "data/places_merged.csv"
    merged_df.to_csv(output_path, index=False)
    
    print(f"\n병합 완료:")
    print(f"- 총 {len(merged_df)}개 장소")
    print(f"- 중복 제거된 장소: {len(existing_df) + len(new_df) - len(merged_df)}개")
    print(f"- 저장 위치: {output_path}")
    
    # 샘플 데이터 출력
    print("\n새로 추가된 장소 샘플:")
    new_places = merged_df[~merged_df['place_id'].isin(existing_df['place_id'])]
    if len(new_places) > 0:
        print(new_places[['place_id', 'name', 'type', 'district']].head())
    else:
        print("새로 추가된 장소가 없습니다.")

if __name__ == "__main__":
    merge_places()