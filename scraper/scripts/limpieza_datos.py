from pymongo import MongoClient

# Conexión a MongoDB
client = MongoClient("mongodb://localhost:27017/")  # si ejecutas fuera del contenedor
db = client["trafico"]
collection = db["eventos"]

# Paso 1: Identificar duplicados
print("Buscando duplicados...")
pipeline = [
    {"$group": {
        "_id": "$uuid",
        "count": {"$sum": 1},
        "docs": {"$push": "$_id"}
    }},
    {"$match": {"count": {"$gt": 1}}}
]

duplicados = list(collection.aggregate(pipeline))
print(f"Encontrados {len(duplicados)} uuids duplicados.")

# Paso 2: Eliminar duplicados
total_eliminados = 0
for dup in duplicados:
    ids = dup["docs"]
    # Mantener uno y eliminar los demás
    ids_to_delete = ids[1:]
    result = collection.delete_many({"_id": {"$in": ids_to_delete}})
    total_eliminados += result.deleted_count

print(f"Eliminados {total_eliminados} documentos duplicados.")

# Paso 3: Ahora sí, crear el índice único
print("Creando índice único en 'uuid'...")
collection.create_index("uuid", unique=True)

print("Limpieza completa ✅")

