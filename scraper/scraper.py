import requests
import time
from pymongo import MongoClient

# Conexión a MongoDB (servicio llamado 'mongo' en docker-compose)
client = MongoClient("mongodb://mongo:27017/")
db = client["trafico"]
collection = db["eventos"]

# Configuración del área geográfica (centro de Santiago)
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

def obtener_eventos_waze():
    url = "https://www.waze.com/live-map/api/georss"
    eventos_totales = 0
    bloque = 0

    while eventos_totales < 10500:
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200:
            data = response.json()
            eventos = data.get("alerts", []) + data.get("irregularities", [])
            if eventos:
                collection.insert_many(eventos)
                eventos_totales += len(eventos)
                bloque += 1
                print(f"Bloque {bloque}: Se guardaron {len(eventos)} eventos. Total acumulado: {eventos_totales}")
            else:
                print("No se encontraron eventos nuevos en este bloque.")
        else:
            print(f"Error en la solicitud: {response.status_code}")

        # Esperar 5 minutos antes del siguiente scraping
        time.sleep(300)

    print("Scraping completo")

if __name__ == "__main__":
    obtener_eventos_waze()


