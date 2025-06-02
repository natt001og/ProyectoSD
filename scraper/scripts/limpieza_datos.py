from pymongo import MongoClient, UpdateOne
from datetime import datetime
from geopy.distance import distance
import pandas as pd

# --- Conexión a MongoDB ---
client = MongoClient("mongodb://localhost:27017/")
db = client["trafico"]
original = db["eventos60000"]  # colección con datos crudos
collection = db["eventos_limpios"]  # colección destino para datos limpios

# --- Copiar datos crudos a colección limpia (preparación) ---
print("Copiando datos originales a colección limpia...")
collection.drop()
collection.insert_many(original.find())

# --- Filtrado: eliminar registros incompletos o erróneos ---
print("Eliminando registros incompletos o erróneos...")
filtro_incompleto = {
    "$or": [
        {"type": {"$exists": False}},
        {"location": {"$exists": False}},
        {"pubMillis": {"$exists": False}},
        {"street": {"$exists": False}},
        {"city": {"$exists": False}},
        {"uuid": {"$exists": False}},
    ]
}
result = collection.delete_many(filtro_incompleto)
print(f"Han sido eliminados {result.deleted_count} registros incompletos o erróneos.")

# --- Eliminación de duplicados por UUID ---
print("Eliminando duplicados por UUID...")
pipeline = [
    {"$group": {"_id": "$uuid", "count": {"$sum": 1}, "docs": {"$push": "$_id"}}},
    {"$match": {"count": {"$gt": 1}}}
]
duplicados = list(collection.aggregate(pipeline))
total_eliminados = 0
for dup in duplicados:
    ids_a_borrar = dup["docs"][1:]  # Conserva solo un documento por UUID
    res = collection.delete_many({"_id": {"$in": ids_a_borrar}})
    total_eliminados += res.deleted_count
print(f"🧹 Eliminados {total_eliminados} duplicados.")

# --- Agrupamiento y unificación de incidentes similares ---
print("Agrupando y unificando incidentes similares (geográfica y temporalmente)...")

eventos = list(collection.find())
visitados = set()
unificados = []

for i, ev1 in enumerate(eventos):
    if ev1["_id"] in visitados:
        continue

    similares = [ev1]
    visitados.add(ev1["_id"])

    for j in range(i + 1, len(eventos)):
        ev2 = eventos[j]
        if ev2["_id"] in visitados:
            continue

        # Verificación proximidad geográfica (menos de 100 metros)
        if "location" in ev1 and "location" in ev2:
            coords1 = (ev1["location"]["y"], ev1["location"]["x"])
            coords2 = (ev2["location"]["y"], ev2["location"]["x"])
            if distance(coords1, coords2).meters > 100:
                continue

            # Verificación proximidad temporal (menos de 5 minutos)
            t1 = datetime.fromtimestamp(ev1["pubMillis"] / 1000)
            t2 = datetime.fromtimestamp(ev2["pubMillis"] / 1000)
            if abs((t1 - t2).total_seconds()) > 300:
                continue

            # Mismo tipo de incidente para agrupar
            if ev1.get("type") == ev2.get("type"):
                similares.append(ev2)
                visitados.add(ev2["_id"])

    # Conservamos solo el primero de los similares, que representará al grupo
    unificados.append(similares[0])

print(f"Incidentes unificados: {len(unificados)}")

# --- Reemplazamos la colección con los incidentes unificados ---
collection.drop()
collection.insert_many(unificados)

# --- Normalización y homogeneización de campos clave ---
print("Normalizando y homogeneizando campos clave...")

updates = []
for evento in collection.find():
    tipo_incidente = evento.get("type", "").lower().strip()
    descripcion = evento.get("street", "").strip()
    comuna = evento.get("city", "").strip()
    timestamp = datetime.fromtimestamp(evento.get("pubMillis", 0) / 1000).isoformat()

    updates.append(UpdateOne(
        {"_id": evento["_id"]},
        {"$set": {
            "tipo_incidente": tipo_incidente,
            "descripcion": descripcion,
            "comuna": comuna,
            "timestamp": timestamp
        }}
    ))

if updates:
    result = collection.bulk_write(updates)
    print(f"Han sido normalizados {result.modified_count} documentos.")

# --- Exportar a TSV ---
print("Exportando datos limpios a TSV...")
datos = list(collection.find({}, {"_id": 0}))
df = pd.DataFrame(datos)
df.to_csv("eventos_limpios.tsv", sep='\t', index=False)
print("Archivo 'eventos_limpios.tsv' exportado correctamente.")

