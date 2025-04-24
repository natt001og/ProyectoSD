import requests
import time
from pymongo import MongoClient

client = MongoClient("mongodb://mongo:27017/")
db = client["trafico"]
collection = db["eventos"]


def obtener_eventos_waze():
    url = "https://www.waze.com/live-map/api/georss"
    # Configuración para scrapear el centro
    params = {
        "top": -33.4250,
        "bottom": -33.4650,
        "left": -70.6950,
        "right": -70.6150,
        "env": "row",
        "types": "alerts,traffic,users"
    }
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://www.waze.com/"
    }

    eventos_totales = 0
    while eventos_totales < 10500:
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200:
            data = response.json()
            eventos = data.get("alerts", []) + data.get("irregularities", [])
            if eventos:
                collection.insert_many(eventos)
                eventos_totales += len(eventos)
                print(f"Se guardaron {len(eventos)} eventos. Total acumulado: {eventos_totales}")
            else:
                print("No se encontraron eventos nuevos en este bloque.")
        else:
            print(f"Error en la solicitud: {response.status_code}")

        # Esperar 10 segundoss antes del siguiente scraping
        time.sleep(10)

    print("Scraping completo")

if __name__ == "__main__":
    obtener_eventos_waze()


