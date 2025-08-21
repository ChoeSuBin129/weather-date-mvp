import csv, json

def load_weather():
    with open("data/raw/weather_today.json", encoding="utf-8") as f:
        return json.load(f)

def load_places():
    with open("data/places.csv", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def load_profile(user_id="u001"):
    with open("data/profiles.csv", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["user_id"] == user_id:
                return row
    return None

def clip(x, lo=-1, hi=1): return max(lo, min(hi, x))

def weather_fit(p, wx):
    score = 0.0
    indoor = int(p["indoor"]) == 1
    rain = float(wx.get("precip_mm") or 0.0)
    wind = float(wx.get("wind_max_mps") or 0.0)
    if rain > 1.0: score += 0.3 if indoor else -0.4
    if wind > 7.0 and p["type"] in ["viewpoint","trail"]: score -= 0.3
    tmax = float(wx.get("temp_max") or 0.0)
    tmin = float(wx.get("temp_min") or 0.0)
    feels = (tmax + tmin) / 2.0
    if 10 <= feels <= 26 and p["type"] in ["park","trail","viewpoint"]:
        score += 0.3
    return clip(score)

def pref_fit(p, prof):
    s = 0.0
    # 활동성 선호도로 실내/실외 선호도 대체
    outdoor_pref = float(prof["active_level"] or 0.5)  # 활동성이 높을수록 실외 선호
    indoor = int(p["indoor"]) == 1
    s += (outdoor_pref if not indoor else (1-outdoor_pref)) * 0.2

    # 성격 유형 점수
    if prof["personality_type"] == "extrovert" and p["extrovert_friendly"] == "yes":
        s += 0.15
    elif prof["personality_type"] == "introvert" and p["extrovert_friendly"] == "no":
        s += 0.15

    # 기존 선호도 점수
    s += (int(p["romantic"])/5.0) * float(prof["romantic_pref"] or 0) * 0.3
    s += (1 - abs((int(p["noise"])-1)/4.0 - float(prof["noise_pref"] or 0))) * 0.15
    s += (1 - abs(int(p["budget_level"]) - float(prof["budget_pref"] or 2))/4.0) * 0.1
    s += (int(p["walk_score"])/5.0) * min(1.0, float(prof["walk_limit_km"] or 1)/3.0) * 0.15

    # 장소 유형 보너스
    if p["type"] in ["park","cafe","museum","trail","viewpoint","heritage","street","market"]:
        s += 0.1
    return clip(s, 0, 1)

def main():
    print("Loading weather data...")
    wx = load_weather()
    print("Weather data:", wx)
    print("Loading profile...")
    prof = load_profile("u001")
    print("Profile:", prof)
    print("Loading places...")
    places = load_places()
    print("Places loaded:", len(places))
    scored = []
    for p in places:
        wf = weather_fit(p, wx)
        pf = pref_fit(p, prof) if prof else 0.5
        final = 0.35*wf + 0.55*pf + 0.10*0.5
        scored.append((final, p, wf, pf))
    scored.sort(reverse=True, key=lambda x: x[0])
    top3 = []
    for final, p, wf, pf in scored[:3]:
        reason = []
        if wf > 0.1: reason.append("날씨와 잘 맞음")
        if pf > 0.6: reason.append("취향 점수 높음")
        if not reason: reason.append("균형 잡힌 선택")
        top3.append({"name": p["name"], "type": p["type"], "score": round(final,3), "reason": " / ".join(reason)})
    with open("data/tmp_top3.json","w",encoding="utf-8") as f:
        json.dump(top3,f,ensure_ascii=False,indent=2)
    print("TOP3 saved: data/tmp_top3.json")

if __name__ == "__main__":
    main()