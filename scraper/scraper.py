import requests
from pymongo import MongoClient, errors
import time

# Conexión a MongoDB
client = MongoClient("mongodb://mongo:27017/")
db = client["trafico"]
collection = db["eventos60000"]

# Crear índice único en 'uuid'
collection.create_index("uuid", unique=True)

# Definir las zonas
zonas = [
    {"top": -33.35, "bottom": -33.45, "left": -70.9, "right": -70.6},   # Centro
    {"top": -33.35, "bottom": -33.45, "left": -70.6, "right": -70.3},   # Este
    {"top": -33.45, "bottom": -33.55, "left": -70.9, "right": -70.6},   # Sur
    {"top": -33.45, "bottom": -33.55, "left": -70.6, "right": -70.3},   # Sureste
    {"top": -33.35, "bottom": -33.45, "left": -71.2, "right": -70.9},   # Oeste
    {"top": -33.45, "bottom": -33.63, "left": -71.2, "right": -70.9},   # Suroeste
]

def capturar_eventos():
    url = "https://www.waze.com/live-map/api/georss"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://www.waze.com/"
    }

    eventos_totales = 0
    vistos = set()

    while eventos_totales < 60000:
        for zona in zonas:
            params = {
                "top": zona["top"],
                "bottom": zona["bottom"],
                "left": zona["left"],
                "right": zona["right"],
                "env": "row",
                "types": "alerts"
            }

            try:
                response = requests.get(url, params=params, headers=headers, timeout=10)
                if response.status_code != 200:
                    print(f"Error en la solicitud ({response.status_code}) en zona {zona}")
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
                        print(f"Zona {zona} - Insertados {eventos_insertados} eventos. Total acumulado: {eventos_totales}")
                    except errors.BulkWriteError as bwe:
                        # Solo cuenta los que sí fueron insertados (los no duplicados)
                        inserted = len(bwe.details.get("writeErrors", []))
                        eventos_totales += len(nuevos_eventos) - inserted
                        print(f"Zona {zona} - Insertados con duplicados. Total acumulado: {eventos_totales}")
                else:
                    print(f"Zona {zona} - No se encontraron eventos nuevos.")

                if eventos_totales >= 60000:
                    print("Objetivo de 60000 eventos alcanzado.")
                    return

                time.sleep(1)  # Evitar hacer muchas solicitudes seguidas

            except requests.exceptions.RequestException as e:
                print(f"Error de conexión: {e}")
                time.sleep(5)  # Esperar un poco antes de reintentar

if __name__ == "__main__":
    capturar_eventos()
