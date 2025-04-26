import requests
from pymongo import MongoClient

# Conexión a MongoDB
client = MongoClient("mongodb://mongo:27017/")
db = client["trafico"]
collection = db["eventos3"]
collection = db["eventos10000"]
>>>>>>> 4a419aab6945a806081e3a323f7ae0f1bf70b3f7

# Crear índice único en 'uuid' para evitar duplicados
collection.create_index("uuid", unique=True)

def capturar_eventos():
    url = "https://www.waze.com/live-map/api/georss"
    
    # Tu zona específica
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

