import random
import time
import requests
import numpy as np

# Configuración
TOTAL_UUIDS = 8000  # Total de UUIDs en tu sistema
MEAN = TOTAL_UUIDS // 2  # Centro de la distribución (p. ej. UUIDs alrededor del 5000 serán más frecuentes)
STD_DEV = TOTAL_UUIDS // 4  # Desviación estándar (ajusta para controlar la dispersión)
CACHE_SERVER_URL = "http://cache:5000/evento"

def generar_uuid_normal():
    """Genera un índice UUID siguiendo una distribución normal."""
    idx = int(np.random.normal(MEAN, STD_DEV))
    idx = max(0, min(idx, TOTAL_UUIDS - 1))  # Asegura que esté en el rango [0, TOTAL_UUIDS-1]
    return f"uuid-{idx:08d}"  # Formato: uuid-00005000 (simula un UUID real)

def generar_trafico():
    """Envía consultas al cache con distribución normal."""
    while True:
        uuid = generar_uuid_normal()
        try:
            response = requests.get(f"{CACHE_SERVER_URL}/{uuid}")
            print(f"Consulta {uuid}: HTTP {response.status_code}")
        except Exception as e:
            print(f"Error consultando {uuid}: {str(e)}")
        
        time.sleep(random.uniform(0.1, 1.0))  # Espera aleatoria entre 0.1s y 1s

if __name__ == "__main__":
    print(f"Generando tráfico con distribución normal (μ={MEAN}, σ={STD_DEV})...")
    generar_trafico()