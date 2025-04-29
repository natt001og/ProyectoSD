import requests
from pymongo import MongoClient

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

    if response.status_code == 200:
        data = response.json()
        alertas = data.get("alerts", [])

        nuevas = 0
        for alerta in alertas:
            try:
                collection.insert_one(alerta)
                nuevas += 1
            except Exception as e:
                if "duplicate key error" not in str(e):
                    print("Error al insertar:", e)

        print(f"{nuevas} nuevas alertas guardadas en MongoDB.")
    else:
        print("Error al obtener datos:", response.status_code)

if _name_ == "_main_":
    capturar_eventos()
