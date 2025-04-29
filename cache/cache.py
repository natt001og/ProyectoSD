from flask import Flask, jsonify
import redis
import json
from pymongo import MongoClient

app = Flask(__name__)
r = redis.Redis(host='redis', port=6379, decode_responses=True)
mongo = MongoClient("mongodb://mongo:27017/")
collection = mongo["trafico"]["eventos10000"]

@app.route("/evento/<uuid>")
def get_evento(uuid):
    # Primero intentamos obtener desde cache
    data = r.get(uuid)
    if data:
        return jsonify({"status": "hit", "evento": json.loads(data)})
    else:
        evento = collection.find_one({"uuid": uuid}, {"_id": 0})
        if evento:
            r.set(uuid, json.dumps(evento), ex=1200)  # TTL = 20 minutos
            return jsonify({"status": "miss", "evento": evento})
        else:
            return jsonify({"status": "miss", "evento": None}), 404

@app.route("/eventos")
def get_uuids():
    eventos = list(collection.find({}, {"uuid": 1, "_id": 0}).limit(10000))
    return jsonify(eventos)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)