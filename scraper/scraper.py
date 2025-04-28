import requests
import time
from pymongo import MongoClient

# Conexión a MongoDB
client = MongoClient("mongodb://mongo:27017/")
db = client["trafico"]
collection = db["eventos10000"]

# Crear índice único en 'uuid' para evitar duplicados
collection.create_index("uuid", unique=True)

# Definimos varias zonas (cada una es un diccionario)
zonas = [
    {
        "top": -33.4125,
        "bottom": -33.4183,
        "left": -70.6699,
        "right": -70.6459
    },
    {
        "top": -33.44737389111507,
        "bottom": -33.451498902049984,
        "left": -70.66786587238313,
        "right": -70.64385473728181
    },
    {
        "top": -33.47545642705913,
        "bottom": -33.47877471207536,
        "left": -70.69757401943208,
        "right": -70.67356288433076
    }
]

headers = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://www.waze.com/"
}

def capturar_eventos():
    url = "https://www.waze.com/live-map/api/georss"
    eventos_totales = 0
    zona_actual = 0  # Comenzamos por la primera zona

    while eventos_totales < 10500:
        # Seleccionamos la zona actual
        params = {
            "top": zonas[zona_actual]["top"],
            "bottom": zonas[zona_actual]["bottom"],
            "left": zonas[zona_actual]["left"],
            "right": zonas[zona_actual]["right"],
            "env": "row",
            "types": "alerts"
        }

        try:
            response = requests.get(url, params=params, headers=headers)

            if response.status_code == 200:
                data = response.json()
                eventos = data.get("alerts", [])

                nuevas = 0
                for alerta in eventos:
                    try:
                        collection.insert_one(alerta)
                        nuevas += 1
                    except Exception as e:
                        if "duplicate key error" not in str(e):
                            print("Error al insertar alerta:", e)

                eventos_totales += nuevas
                print(f"Zona {zona_actual+1}: Se guardaron {nuevas} nuevas alertas. Total acumulado: {eventos_totales}")
            else:
                print(f"Error en la solicitud: {response.status_code}")

        except Exception as e:
            print(f"Error en la solicitud a la API:", e)

        # Cambiar a la siguiente zona
        zona_actual = (zona_actual + 1) % len(zonas)

        # Espera un poquito antes de la siguiente consulta
        time.sleep(5)

    print("¡Captura completa! Se alcanzaron más de 10.500 eventos.")

if __name__ == "__main__":
    capturar_eventos()

