import requests
import time
from pymongo import MongoClient

client = MongoClient("mongodb://mongo:27017/")
db = client["trafico"]
collection = db["eventos3"]


def obtener_eventos_waze():
    url = "https://www.waze.com/live-map/api/georss"
    # Configuración para scrapear el centro
    params = {
        "top": -34.983312784762894,
        "bottom": -34.98977870345623,
        "left": -71.2445515394211,
        "right": -71.22054040431978,
        "env": "row",
        "types": "alerts"
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
            eventos = data.get("alerts", [])
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


