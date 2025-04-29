import time
import random
import requests
import numpy as np

API_URL = "http://cache:5000/evento"  # La API de caché escucha en este endpoint

# Puedes cambiar esto a "zipf" para probar otro modelo
MODELO = "zipf"
TOTAL_CONSULTAS = 1000

def obtener_uuid_random_poisson(eventos, lam=10):
    idx = int(np.random.exponential(lam))
    return eventos[idx % len(eventos)]["uuid"]

def obtener_uuid_random_zipf(eventos, a=2.0):
    idx = np.random.zipf(a) - 1
    return eventos[idx % len(eventos)]["uuid"]

def main():
    # Obtener lista de eventos desde la API
    response = requests.get("http://cache:5000/eventos")
    if response.status_code != 200:
        print("No se pudo obtener eventos.")
        return

    eventos = response.json()
    print(f"Se obtuvieron {len(eventos)} eventos.")

    for _ in range(TOTAL_CONSULTAS):
        if MODELO == "poisson":
            uuid = obtener_uuid_random_poisson(eventos)
        else:
            uuid = obtener_uuid_random_zipf(eventos)

        r = requests.get(f"{API_URL}/{uuid}")
        print(f"[{MODELO.upper()}] Consulta UUID {uuid}: {r.json()['status']}")
        time.sleep(0.1)

if __name__ == "__main__":
    main()

