from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)  # 모든 도메인에서의 요청 허용

def load_places():
    return pd.read_csv('../data/places.csv')

def calculate_match_score(place, user_prefs):
    score = 0.0
    weights = {
        'location': 0.15,  # 같은 구면 점수 부여
        'personality': 0.15,  # 성격 유형과 장소 특성 매칭
        'drinking': 0.1,  # 음주 가능 여부
        'active': 0.1,  # 활동성 선호도
        'noise': 0.1,  # 소음 레벨 선호도
        'romantic': 0.15,  # 로맨틱한 분위기 선호도
        'budget': 0.15,  # 비용 선호도
        'walk': 0.1,  # 도보 거리 선호도
    }

    # 위치 점수
    if place['district'] == user_prefs['district']:
        score += weights['location']

    # 성격 유형 점수
    if user_prefs['personality'] == 'extrovert' and place['extrovert_friendly'] == 'yes':
        score += weights['personality']
    elif user_prefs['personality'] == 'introvert' and place['extrovert_friendly'] == 'no':
        score += weights['personality']

    # 음주 가능 여부
    if user_prefs['drinking'] == 'yes' and place['alcohol_available'] == 'yes':
        score += weights['drinking']
    elif user_prefs['drinking'] == 'no' and place['alcohol_available'] == 'no':
        score += weights['drinking']

    # 활동성 점수 (noise를 활동성 지표로 사용)
    activity_score = abs(float(user_prefs['active']) - (float(place['noise']) / 5))
    score += weights['active'] * (1 - activity_score)

    # 소음 레벨 선호도
    noise_score = abs(float(user_prefs['noise']) - (float(place['noise']) / 5))
    score += weights['noise'] * (1 - noise_score)

    # 로맨틱한 분위기 선호도
    romantic_score = abs(float(user_prefs['romantic']) - (float(place['romantic']) / 5))
    score += weights['romantic'] * (1 - romantic_score)

    # 비용 선호도
    budget_score = abs(int(user_prefs['budget']) - int(place['budget_level']))
    score += weights['budget'] * (1 - budget_score / 4)

    # 도보 거리 선호도
    if int(place['walk_score']) <= int(user_prefs['walk']):
        score += weights['walk']

    return score

@app.route('/api/recommend', methods=['POST'])
def recommend():
    try:
        user_prefs = request.json
        places_df = load_places()
        
        # 각 장소의 매칭 점수 계산
        places_df['score'] = places_df.apply(
            lambda place: calculate_match_score(place, user_prefs), axis=1
        )
        
        # 상위 5개 장소 선택
        top_places = places_df.nlargest(5, 'score')
        
        recommendations = []
        for _, place in top_places.iterrows():
            recommendations.append({
                'name': place['name'],
                'type': place['type'],
                'district': place['district'],
                'score': round(place['score'], 3),
                'tags': place['tags'],
                'indoor': place['indoor'] == 1,
                'budget_level': int(place['budget_level'])
            })

        return jsonify({
            'success': True,
            'recommendations': recommendations,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
