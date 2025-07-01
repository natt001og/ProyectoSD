from elasticsearch import Elasticsearch
import redis
import os
import logging
import time
from datetime import datetime, timedelta, time as dtime
import json

# Configuración robusta para Elasticsearch
ELASTICSEARCH_URL = os.getenv("ELASTICSEARCH_URL", "http://elasticsearch:9200")
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
UPDATE_INTERVAL = int(os.getenv("UPDATE_INTERVAL", 300))  # 5 minutos por defecto

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Configuración avanzada del cliente Elasticsearch
es = Elasticsearch(
    ELASTICSEARCH_URL,
    http_auth=None,
    verify_certs=False,
    timeout=30,
    max_retries=3,
    retry_on_timeout=True,
    sniff_on_start=True,
    sniff_on_connection_fail=True,
    sniff_timeout=60,
    headers={
        "Accept": "application/vnd.elasticsearch+json; compatible-with=8",
        "Content-Type": "application/json"
    }
)

# Configuración robusta para Redis
r = redis.Redis(
    host=REDIS_HOST,
    port=6379,
    decode_responses=True,
    socket_timeout=5,
    socket_connect_timeout=5,
    retry_on_timeout=True,
    health_check_interval=30
)

def get_top_data():
    try:
        query_incidentes = {
            "size": 0,
            "query": {
                "range": {
                    "dia": {
                        "gte": (datetime.now() - timedelta(days=1)).date().isoformat()
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

        query_comunas = {
            "size": 0,
            "query": {
                "range": {
                    "dia": {
                        "gte": (datetime.now() - timedelta(days=1)).date().isoformat()
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

        res_incidentes = es.search(
            index="eventos-temporales",
            query=query_incidentes["query"],
            aggs=query_incidentes["aggs"],
            size=query_incidentes["size"]
        )
        res_comunas = es.search(
            index="eventos-por-comuna",
            query=query_comunas["query"],
            aggs=query_comunas["aggs"],
            size=query_comunas["size"]
        )

        top_incidentes = [bucket["key"] for bucket in res_incidentes["aggregations"]["top_incidentes"]["buckets"]]
        top_comunas = [bucket["key"] for bucket in res_comunas["aggregations"]["top_comunas"]["buckets"]]

        return top_incidentes, top_comunas

    except Exception as e:
        logging.error(f"Error al consultar Elasticsearch: {e}")
        return [], []


def cache_data(incidentes, comunas):
    try:
        hoy = datetime.now().date()
        inicio_dia = datetime.combine(hoy, dtime.min)

        for incidente in incidentes:
            query = {
                "bool": {
                    "must": [
                        {"term": {"tipo_incidente.keyword": incidente}},
                        {"range": {"dia": {"gte": inicio_dia.isoformat(), "lte": datetime.now().isoformat()}}}
                    ]
                }
            }
            results = es.search(index="eventos-temporales", query=query, size=50)
            r.setex(f"top:incidente:{incidente}", 1800, json.dumps([hit["_source"] for hit in results["hits"]["hits"]]))
        
        for comuna in comunas:
            query = {
                "bool": {
                    "must": [
                        {"term": {"comuna.keyword": comuna}},
                        {"range": {"dia": {"gte": inicio_dia.isoformat(), "lte": datetime.now().isoformat()}}}
                    ]
                }
            }
            results = es.search(index="eventos-por-comuna", query=query, size=50)
            r.setex(f"top:comuna:{comuna}", 1800, json.dumps([hit["_source"] for hit in results["hits"]["hits"]]))

        logging.info("Datos cacheados correctamente")


    except Exception as e:
        logging.error(f"Error al guardar en Redis: {e}")


def main():
    """Ejecución principal"""
    logging.info("Iniciando cache-worker")
    while True:
        try:
            incidentes, comunas = get_top_data()
            cache_data(incidentes, comunas)
            time.sleep(UPDATE_INTERVAL)
        except Exception as e:
            logging.error(f"Error en main: {str(e)}")
            time.sleep(30)

if __name__ == "__main__":
    main()
