import requests
import json
import os
from datetime import datetime

#URL de la api a la que llaman las peticiones GET
url = "https://www.waze.com/live-map/api/georss"
# Coordenadas para la parte de RM a scrapear
params = {
    "top": -33.4466,
    "bottom": -33.4581,
    "left": -70.6950,
    "right": -70.6274,
    "env": "row",
    "types": "alerts,traffic,users"
}
headers = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://www.waze.com/"
}

response = requests.get(url, params=params, headers=headers)

if response.status_code == 200:
    raw_data = response.json()
    
    # Crea la carpeta 'scraper/data' si no existe
    os.makedirs("scraper/data", exist_ok=True)

    # Usa timestamp para no sobreescribir archivos
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"scraper/data/waze_data_{timestamp}.json"

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(raw_data, f, indent=2, ensure_ascii=False)

    print(f" Datos guardados correctamente en {filename}")
else:
    print(f"Error al obtener datos: {response.status_code}")
