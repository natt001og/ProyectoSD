import time
import requests
import numpy as np

API_URL = "http://cache:5000/evento"  # La API de caché escucha en este endpoint

MODELO = "poisson"
TOTAL_CONSULTAS = 70000

def esperar_cache_disponible(url, reintentos=10, espera=2):
    for intento in range(reintentos):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return response
        except requests.exceptions.ConnectionError:
            print(f"Intento {intento+1}/{reintentos}: cache no disponible aún, esperando {espera}s...")
            time.sleep(espera)
    raise Exception("No se pudo conectar con el cache luego de varios intentos.")

def obtener_uuid_random_poisson(eventos, lam=10):
    idx = int(np.random.exponential(lam))
    return eventos[idx % len(eventos)]["uuid"]

def obtener_uuid_random_zipf(eventos, a=2.0):
    idx = np.random.zipf(a) - 1
    return eventos[idx % len(eventos)]["uuid"]

def main():
    # Registrar el tiempo de inicio
    inicio = time.time()

    response = esperar_cache_disponible("http://cache:5000/eventos")
    eventos = response.json()
    print(f"Se obtuvieron {len(eventos)} eventos.")

    hits = 0
    misses = 0

    for _ in range(TOTAL_CONSULTAS):
        if MODELO == "poisson":
            uuid = obtener_uuid_random_poisson(eventos)
        else:
            uuid = obtener_uuid_random_zipf(eventos)

        r = requests.get(f"{API_URL}/{uuid}")
        estado = r.json()["status"]
        print(f"[{MODELO.upper()}] Consulta UUID {uuid}: {estado}")

        if estado == "hit":
            hits += 1
        else:
            misses += 1

        time.sleep(0.01)

    # Calcular el tiempo total
    fin = time.time()
    tiempo_total = fin - inicio

    print(f"\nResumen final: {hits} hits, {misses} misses")
    print(f"Tiempo total de las consultas: {tiempo_total:.2f} segundos")

if __name__ == "__main__":
    main()
