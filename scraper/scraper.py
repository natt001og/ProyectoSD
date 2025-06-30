import requests
import time
from pymongo import MongoClient
from pymongo.errors import BulkWriteError

# Conexión a MongoDB
client = MongoClient("mongodb://mongo:27017/")
db = client["trafico"]
collection = db["eventos10000"]

# Crear índice único en 'uuid' para evitar duplicados
collection.create_index("uuid", unique=True)

def capturar_eventos():
    url = "https://www.waze.com/live-map/api/georss"
    
    params = {
        "top": -33.44067122117045,
        "bottom": -33.44347517754554,
        "left": -70.6693357229233,
        "right": -70.64532458782197,
        "env": "row",
        "types": "alerts"
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://www.waze.com/"
    }

    eventos_totales = 0
    iteraciones_sin_nuevos = 0

    while eventos_totales < 10500 and iteraciones_sin_nuevos < 5:
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200:
            data = response.json()
            eventos = data.get("alerts", [])
            if eventos:
                try:
                    result = collection.insert_many(eventos, ordered=False)
                    insertados = len(result.inserted_ids)
                    eventos_totales += insertados
                    print(f"{insertados} insertados. Total acumulado: {eventos_totales}")
                    iteraciones_sin_nuevos = 0
                except BulkWriteError as bwe:
                    errores = bwe.details.get("writeErrors", [])
                    duplicados = sum(1 for e in errores if e.get("code") == 11000)
                    insertados = len(eventos) - duplicados
                    eventos_totales += insertados
                    print(f"{insertados} insertados, {duplicados} duplicados. Total acumulado: {eventos_totales}")
                    if insertados == 0:
                        iteraciones_sin_nuevos += 1
            else:
                print("No se encontraron eventos.")
                iteraciones_sin_nuevos += 1
        else:
            print(f"Error en la solicitud: {response.status_code}")
            break
        
        time.sleep(2)  # Espera opcional para no saturar el servidor

    print("Scraper finalizado.")

if __name__ == "__main__":
    capturar_eventos()

