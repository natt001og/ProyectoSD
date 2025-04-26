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
    
    # Tu zona específica
    params = {
        "top": -33.41251384431723,
        "bottom": -33.41839213779204,
        "left": -70.66993653774263,
        "right": -70.64592540264131,
        "env": "row",
        "types": "alerts"
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://www.waze.com/"
    }

    response = requests.get(url, params=params, headers=headers)

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

if __name__ == "__main__":
    capturar_eventos()

