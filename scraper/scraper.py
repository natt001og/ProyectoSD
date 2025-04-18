import requests
import json

params = {
    "bottom": -33.5000,
    "left": -70.8000,
    "top": -33.3000,
    "right": -70.6000,
    "types": "alerts,traffic,irregularities"
}

url = "https://www.waze.com/row-rtserver/web/TGeoRSS"
headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(url, params=params, headers=headers)
data = response.json()

with open("waze_data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4, ensure_ascii=False)

print("✅ Datos guardados en waze_data.json")
