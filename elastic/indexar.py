import os
import csv
from elasticsearch import Elasticsearch, helpers

es = Elasticsearch("http://localhost:9200")

if not es.ping():
    print("No se pudo conectar a Elasticsearch")
    exit(1)
else:
    print("Conectado a Elasticsearch OK")

index_name = "incidentess"

if not es.indices.exists(index=index_name):
    es.indices.create(index=index_name)
    print(f"Índice '{index_name}' creado.")

file_path = os.path.join("..", "docker-pig", "eventos_limpios.tsv", "part-r-00000")

def generate_actions(file_path):
    with open(file_path, encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        for row in reader:
            doc = {
                "comuna": row[0],
                "tipo_incidente": row[1],
                "timestamp": int(row[2]),
                "campo_vacio": row[3],
                "numero_decimal": float(row[4]) if row[4] else 0.0,
                "numero_entero": int(row[5]),
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
