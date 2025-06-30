import os
import csv
from elasticsearch import Elasticsearch, helpers

# Conexión a Elasticsearch
es = Elasticsearch("http://localhost:9200")

try:
    es.info()
    print("Conectado a Elasticsearch OK")
except Exception as e:
    print("No se pudo conectar a Elasticsearch:", e)
    exit(1)

index_name = "prueba1"

# Crear índice si no existe
if not es.indices.exists(index=index_name):
    es.indices.create(index=index_name)
    print(f"Índice '{index_name}' creado.")

# Construcción de ruta absoluta del archivo part-r-00000
file_path = os.path.join(os.path.dirname(__file__), "..", "docker-pig", "eventos_limpios.tsv", "part-r-00000")
file_path = os.path.abspath(file_path)
print(f"Buscando archivo en: {file_path}")

# Verificar si el archivo existe antes de abrir
if not os.path.isfile(file_path):
    print(f"Archivo no encontrado: {file_path}")
    exit(1)

def generate_actions(file_path):
    with open(file_path, encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        for row in reader:
            # Validar que fila tenga al menos 7 columnas para evitar errores
            if len(row) < 7:
                continue
            doc = {
                "comuna": row[0],
                "tipo_incidente": row[1],
                "timestamp": int(row[2]) if row[2].isdigit() else 0,
                "campo_vacio": row[3],
                "numero_decimal": float(row[4]) if row[4] else 0.0,
                "numero_entero": int(row[5]) if row[5].isdigit() else 0,
                "uuid": row[6],
            }
            yield {
                "_index": index_name,
                "_source": doc
            }

try:
    result = helpers.bulk(es, generate_actions(file_path))
    print(f"Se indexaron {result[0]} documentos.")
except Exception as e:
    print("Error en indexación:", e)
