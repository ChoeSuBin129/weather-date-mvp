from datetime import date
import requests, json, os

BASE = "https://api.open-meteo.com/v1/forecast"
params = {
    "latitude": 37.5665, "longitude": 126.9780,  # 서울
    "daily": ["weathercode","temperature_2m_max","temperature_2m_min","precipitation_sum","windspeed_10m_max","cloudcover_mean"],
    "timezone": "Asia/Seoul"
}
os.makedirs("data/raw", exist_ok=True)
print("Fetching weather data...")
r = requests.get(BASE, params=params, timeout=20)
print("Response status:", r.status_code)
r.raise_for_status()
daily = r.json().get("daily", {})
print("Got daily data:", daily)
out = {
    "date": str(date.today()),
    "weathercode": daily.get("weathercode", [None])[0],
    "temp_max": daily.get("temperature_2m_max", [None])[0],
    "temp_min": daily.get("temperature_2m_min", [None])[0],
    "precip_mm": daily.get("precipitation_sum", [None])[0],
    "wind_max_mps": daily.get("windspeed_10m_max", [None])[0],
    "cloud_mean": daily.get("cloudcover_mean", [None])[0],
}
with open("data/raw/weather_today.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)
print("saved: data/raw/weather_today.json")
