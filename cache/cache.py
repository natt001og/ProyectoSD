from flask import Flask, jsonify
import redis
import json
from pymongo import MongoClient
from datetime import datetime, timedelta

app = Flask(__name__)
r = redis.Redis(host='redis', port=6379, decode_responses=True)
mongo = MongoClient("mongodb://mongo:27017/")
collection = mongo["trafico"]["eventos10000"]

# Endpoints existentes
@app.route("/evento/<uuid>")
def get_evento(uuid):
    """Endpoint existente para buscar eventos individuales por UUID"""
    data = r.get(uuid)
    if data:
        return jsonify({
            "status": "hit", 
            "source": "cache",
            "evento": json.loads(data)
        })
    else:
        evento = collection.find_one({"uuid": uuid}, {"_id": 0})
        if evento:
            r.set(uuid, json.dumps(evento), ex=1200)  # TTL = 20 minutos
            return jsonify({
                "status": "miss", 
                "source": "database",
                "evento": evento
            })
        else:
            return jsonify({
                "status": "miss",
                "evento": None
            }), 404

@app.route("/eventos")
def get_uuids():
    """Endpoint existente para obtener lista de UUIDs"""
    eventos = list(collection.find({}, {"uuid": 1, "_id": 0}).limit(1000))
    return jsonify(eventos)

# Nuevos endpoints para datos pre-cacheados
@app.route("/cache/top-incidentes")
def get_top_incidentes():
    """
    Devuelve los tipos de incidentes más frecuentes pre-cacheados
    Formato: { "incidente1": [eventos], "incidente2": [eventos], ... }
    """
    incidentes = {}
    for key in r.keys("top:incidente:*"):
        incidente = key.split(":")[2]
        try:
            incidentes[incidente] = json.loads(r.get(key))
        except Exception as e:
            print(f"Error al parsear datos para {incidente}: {str(e)}")
    
    return jsonify({
        "status": "success",
        "count": len(incidentes),
        "data": incidentes
    })

@app.route("/cache/top-comunas")
def get_top_comunas():
    """
    Devuelve las comunas más activas pre-cacheadas
    Formato: { "comuna1": [eventos], "comuna2": [eventos], ... }
    """
    comunas = {}
    for key in r.keys("top:comuna:*"):
        comuna = key.split(":")[2]
        try:
            comunas[comuna] = json.loads(r.get(key))
        except Exception as e:
            print(f"Error al parsear datos para {comuna}: {str(e)}")
    
    return jsonify({
        "status": "success",
        "count": len(comunas),
        "data": comunas
    })

@app.route("/cache/stats")
def get_cache_stats():
    """Estadísticas del estado del caché"""
    stats = {
        "total_keys": len(r.keys()),
        "top_incidentes": len(r.keys("top:incidente:*")),
        "top_comunas": len(r.keys("top:comuna:*")),
        "individual_events": len(r.keys("evento:*")),  # Si usas este patrón
        "memory_usage": r.info("memory")["used_memory_human"]
    }
    return jsonify(stats)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)