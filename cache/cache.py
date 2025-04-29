from flask import Flask, request, jsonify
import redis
from pymongo import MongoClient
import json

app = Flask(__name__)

# Conexión a Redis
redis_client = redis.StrictRedis(host='redis', port=6379, decode_responses=True)

# Conexión a MongoDB
mongo_client = MongoClient('mongodb://mongo:27017/')
db = mongo_client['trafico']
collection = db['eventos10000']  # Asegúrate del nombre correcto de tu colección

@app.route('/evento/<uuid>', methods=['GET'])
def get_event(uuid):
    # Primero intentar obtener desde cache
    evento = redis_client.get(uuid)
    if evento:
        print(f"Cache HIT para {uuid}")
        return jsonify(json.loads(evento)), 200

    # Si no está en cache, buscar en MongoDB
    print(f"Cache MISS para {uuid}")
    evento_db = collection.find_one({"uuid": uuid})
    if evento_db:
        evento_db["_id"] = str(evento_db["_id"])  # Mongo devuelve un ObjectId que no es serializable
        redis_client.set(uuid, json.dumps(evento_db))  # Guardar en cache
        return jsonify(evento_db), 200
    else:
        return jsonify({"error": "Evento no encontrado"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
