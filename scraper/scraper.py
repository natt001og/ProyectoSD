import requests
from pymongo import MongoClient, errors

# Conexión a MongoDB
client = MongoClient("mongodb://mongo:27017/")
db = client["trafico"]
collection = db["eventos10000"]

# Crear índice único en 'uuid'
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
    vistos = set()

    while eventos_totales < 10500:
        response = requests.get(url, params=params, headers=headers)
        if response.status_code != 200:
            print(f"Error en la solicitud: {response.status_code}")
            continue

        data = response.json()
        eventos = data.get("alerts", [])

        nuevos_eventos = []
        for e in eventos:
            uuid = e.get("uuid")
            if uuid and uuid not in vistos:
                vistos.add(uuid)
                nuevos_eventos.append(e)

        if nuevos_eventos:
            try:
                result = collection.insert_many(nuevos_eventos, ordered=False)
                eventos_insertados = len(result.inserted_ids)
                eventos_totales += eventos_insertados
                print(f"Insertados {eventos_insertados} eventos. Total acumulado: {eventos_totales}")
            except errors.BulkWriteError as bwe:
                # Solo cuenta los que sí fueron insertados
                inserted = len(bwe.details.get("writeErrors", []))
                eventos_totales += len(nuevos_eventos) - inserted
                print(f"Insertados con duplicados. Total acumulado: {eventos_totales}")
        else:
            print("No se encontraron eventos nuevos.")

if __name__ == "__main__":
    capturar_eventos()
