from elasticsearch import Elasticsearch, helpers
import csv
from datetime import datetime, timedelta

es = Elasticsearch("http://localhost:9200")

try:
    es.info()
    print("Conectado a Elasticsearch OK")
except Exception as e:
    print("No se pudo conectar a Elasticsearch:", e)
    exit(1)

DATA_CRUDO_FILE = "docker-pig/data.tsv"
TSV_COMUNA = "docker-pig/conteo_por_comuna_tipo"
TSV_TEMPORAL = "docker-pig/conteo_temporal"

def parse_date(dia_str):
    try:
        # Convertir días desde epoch (1/1/1970) a fecha ISO
        days = int(float(dia_str))
        date = datetime(1970, 1, 1) + timedelta(days=days)
        return date.strftime('%Y-%m-%d')  # Formato ISO que Elasticsearch entiende
    except (ValueError, TypeError):
        print(f"Warning: No se pudo convertir días desde epoch: '{dia_str}'")
        return None

def create_index_eventos_temporales():
    if es.indices.exists(index='eventos-temporales'):
        es.indices.delete(index='eventos-temporales')
        print("Índice 'eventos-temporales' eliminado")

    mapping = {
        "mappings": {
            "properties": {
                "dia": {
                    "type": "date",
                    "format": "strict_date"  # Solo formato YYYY-MM-DD
                },
                "tipo_incidente": {"type": "keyword"},
                "total_eventos": {"type": "integer"},
                "avg_votos": {"type": "float"}
            }
        }
    }
    es.indices.create(index='eventos-temporales', body=mapping)
    print("Índice 'eventos-temporales' creado con mapping date en 'dia'")

def index_tsv_data(file_path, index_name, headers, parse_date_field=None):
    print(f"Indexando {file_path} en {index_name}...")
    actions = []
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t', fieldnames=headers)
        for i, doc in enumerate(reader):
            try:
                # Convertir valores numéricos
                for k, v in doc.items():
                    if v == '' or v is None:
                        doc[k] = None
                    else:
                        try:
                            if '.' in v:
                                doc[k] = float(v)
                            else:
                                doc[k] = int(v)
                        except ValueError:
                            pass  # Mantener como string si no es número

                # Procesar campo de fecha si existe
                if parse_date_field and parse_date_field in doc and doc[parse_date_field] is not None:
                    formatted_date = parse_date(doc[parse_date_field])
                    if formatted_date:
                        doc[parse_date_field] = formatted_date
                    else:
                        print(f"Documento {i} omitido - fecha inválida: {doc[parse_date_field]}")
                        continue

                actions.append({
                    "_index": index_name,
                    "_source": doc
                })
            except Exception as e:
                print(f"Error procesando documento {i}: {e}")
                continue

    if actions:
        try:
            success, failed = helpers.bulk(es, actions, stats_only=False, raise_on_error=False)
            print(f"Indexados {success} documentos, {len(failed) if failed else 0} fallidos")
            if failed:
                print("Errores de indexación (primeros 5):")
                for fail in failed[:5]:
                    print(fail)
        except Exception as e:
            print(f"Error durante bulk index: {e}")
    else:
        print(f"No se encontró ningún documento válido en {file_path} para indexar.")

def index_data_cruda(file_path, index_name):
    print(f"Indexando datos crudos desde {file_path} en {index_name}...")
    actions = []
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for i, doc in enumerate(reader):
            try:
                actions.append({
                    "_index": index_name,
                    "_source": doc
                })
            except Exception as e:
                print(f"Error procesando documento crudo {i}: {e}")

    if actions:
        try:
            success, failed = helpers.bulk(es, actions, stats_only=False, raise_on_error=False)
            print(f"Datos crudos: {success} indexados, {len(failed) if failed else 0} fallidos")
        except Exception as e:
            print(f"Error durante bulk index de datos crudos: {e}")
    else:
        print(f"No se encontró ningún documento válido en {file_path} para indexar.")

if __name__ == "__main__":
    headers_comuna = ["comuna", "tipo_incidente", "cantidad_eventos", "avg_votos", "avg_confiabilidad"]
    headers_temporal = ["dia", "tipo_incidente", "total_eventos", "avg_votos"]

    index_data_cruda(DATA_CRUDO_FILE, "datos-crudos")
    index_tsv_data(TSV_COMUNA, "eventos-por-comuna", headers_comuna)

    create_index_eventos_temporales()
    index_tsv_data(TSV_TEMPORAL, "eventos-temporales", headers_temporal, parse_date_field="dia")