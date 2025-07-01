import os
import logging
from datetime import datetime, timedelta
from elasticsearch import Elasticsearch
import redis
import json
import time

# Configuración
ELASTICSEARCH_URL = os.getenv("ELASTICSEARCH_URL", "http://elasticsearch:9200")
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
UPDATE_INTERVAL = int(os.getenv("UPDATE_INTERVAL", 300))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Elasticsearch: fuerza usar versión 8 del protocolo (ajusta según tu versión cliente)
es = Elasticsearch(ELASTICSEARCH_URL, api_version="8.0")

r = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)

def get_top_data():
    try:
        res_fecha_max = es.search(
            index="eventos-temporales",
            body={
                "size": 0,
                "aggs": {
                    "fecha_maxima": {
                        "max": {
                            "field": "dia"
                        }
                    }
                }
            }
        )
        fecha_max = res_fecha_max.get("aggregations", {}).get("fecha_maxima", {}).get("value_as_string", None)
        if not fecha_max:
            logging.warning("No se encontró fecha máxima en eventos-temporales.")
            return [], []

        query_incidentes = {
            "size": 0,
            "query": {
                "range": {
                    "dia": {
                        "gte": fecha_max
                    }
                }
            },
            "aggs": {
                "top_incidentes": {
                    "terms": {
                        "field": "tipo_incidente.keyword",
                        "size": 5
                    }
                }
            }
        }

        res_fecha_max_comunas = es.search(
            index="eventos-por-comuna",
            body={
                "size": 0,
                "aggs": {
                    "fecha_maxima": {
                        "max": {
                            "field": "dia"
                        }
                    }
                }
            }
        )
        fecha_max_comunas = res_fecha_max_comunas.get("aggregations", {}).get("fecha_maxima", {}).get("value_as_string", None)
        if not fecha_max_comunas:
            logging.warning("No se encontró fecha máxima en eventos-por-comuna.")
            return [], []

        query_comunas = {
            "size": 0,
            "query": {
                "range": {
                    "dia": {
                        "gte": fecha_max_comunas
                    }
                }
            },
            "aggs": {
                "top_comunas": {
                    "terms": {
                        "field": "comuna.keyword",
                        "size": 3
                    }
                }
            }
        }

        res_incidentes = es.search(index="eventos-temporales", body=query_incidentes)
        res_comunas = es.search(index="eventos-por-comuna", body=query_comunas)

        top_incidentes = [b["key"] for b in res_incidentes.get("aggregations", {}).get("top_incidentes", {}).get("buckets", [])]
        top_comunas = [b["key"] for b in res_comunas.get("aggregations", {}).get("top_comunas", {}).get("buckets", [])]

        return top_incidentes, top_comunas

    except Exception as e:
        logging.error(f"Error al consultar Elasticsearch: {e}")
        return [], []

def cache_data(incidentes, comunas):
    try:
        for incidente in incidentes:
            query = {
                "query": {
                    "bool": {
                        "must": [
                            {"term": {"tipo_incidente.keyword": incidente}},
                            {"range": {
                                "dia": {"gte": (datetime.now() - timedelta(hours=6)).isoformat()}
                            }}
                        ]
                    }
                },
                "size": 50
            }
            results = es.search(index="eventos-temporales", body=query)
            r.setex(f"top:incidente:{incidente}", 1800, json.dumps([hit["_source"] for hit in results["hits"]["hits"]]))

        for comuna in comunas:
            query = {
                "query": {
                    "bool": {
                        "must": [
                            {"term": {"comuna.keyword": comuna}},
                            {"range": {
                                "dia": {"gte": (datetime.now() - timedelta(hours=6)).isoformat()}
                            }}
                        ]
                    }
                },
                "size": 50
            }
            results = es.search(index="eventos-por-comuna", body=query)
            r.setex(f"top:comuna:{comuna}", 1800, json.dumps([hit["_source"] for hit in results["hits"]["hits"]]))

        logging.info(f"Cached {len(incidentes)} incident types and {len(comunas)} communes")

    except Exception as e:
        logging.error(f"Error al guardar en Redis: {e}")

def main():
    logging.info(">>>> Inició el main() del cache worker")
    while True:
        try:
            logging.info("Iniciando ciclo de pre-caching...")
            top_incidentes, top_comunas = get_top_data()
            cache_data(top_incidentes, top_comunas)
        except Exception as e:
            logging.error(f"Error en el ciclo principal: {e}")
        time.sleep(UPDATE_INTERVAL)

if __name__ == "__main__":
    main()
